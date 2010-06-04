#include "Url.h"

#include <cassert>
#include <fstream> 

#ifndef WIN32
#include <unicode/ustring.h>
#endif

#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>

namespace fs = boost::filesystem;

#if BOOST_VERSION <= 103500
#define is_regular_file is_regular
#endif

std::ostream& operator <<(std::ostream& os, const CUrl& url)
{ 
  os << static_cast<const GURL&>(url);

  return os;
}

void CUrl::Expose(void)
{
  py::class_<CUrl>("Url", py::init<>())
    .def(py::init<const std::string>())
    .def(py::init<const std::wstring>())
    .def(py::init<const CUrl>())

    .def(py::self == py::self)
    .def(py::self != py::self)
    .def(py::self < py::self)

    .def(str(py::self))

    .def("__nonzero__", &CUrl::operator bool)

    .def("empty", &CUrl::IsEmpty)

    .def("join", &CUrl::ResolveA)
    .def("join", &CUrl::ResolveW)

    .def("spec", &CUrl::GetSpec, (py::arg("raw") = false))
    .def("isstandard", &CUrl::IsStandard)

    .add_property("scheme", &CUrl::GetScheme)
    .add_property("username", &CUrl::GetUsername)
    .add_property("password", &CUrl::GetPassword)
    .add_property("hostname", &CUrl::GetHost)
    .add_property("port", &CUrl::GetPort)
    .add_property("path", &CUrl::GetPath)
    .add_property("query", &CUrl::GetQuery)
    .add_property("fragment", &CUrl::GetRef)

    .add_property("filename", &CUrl::GetFilename)
    .add_property("domain", &CUrl::GetDomain)

    .def("schemeis", &CUrl::SchemeIs)
    .def("domainis", &CUrl::DomainIs)

    .add_property("host", &CUrl::GetWithEmptyPath)
    .add_property("origin", &CUrl::GetOrigin)
    .add_property("hostisip", &CUrl::HostIsIPAddress)
    .add_property("request", &CUrl::PathForRequest)
    ;
}

const string16 CUrl::to_string16(const std::wstring& str)
{
#ifdef WIN32
  return str;
#else
  std::vector<UChar> buf(str.size()+1);
  int32_t len = 0;
  UErrorCode err = U_ZERO_ERROR;

  UChar *s = u_strFromUTF32(&buf[0], buf.size(), &len, (const UChar32 *) str.c_str(), str.size(), &err);

  return string16(s, len);
#endif
}

const CUrl::DomainSet CUrl::LoadTldNames(void)
{
  const std::string FILENAME = "effective_tld_names.dat";

  fs::path filepath = FILENAME;

  if (!fs::is_regular_file(filepath))
  {
    PyObject *paths = ::PySys_GetObject("path");

    assert(PyList_Check(paths));

    for (Py_ssize_t i=0; i<PyList_GET_SIZE(paths); i++)
    {
      PyObject *item = PyList_GET_ITEM(paths, i);

      assert(PyString_Check(item));

      filepath = PyString_AS_STRING(item);

      if (fs::is_directory(filepath))
      {
        filepath /= FILENAME;

        if (fs::is_regular_file(filepath))        
          break;        
      }    
    }
  }

  DomainSet domains;

  if (!fs::is_regular_file(filepath)) return domains;

  std::ifstream datafile(filepath.string().c_str());
  
  std::string line;

  while (std::getline(datafile, line))
  {
    boost::trim(line);

    if (line.empty()) continue; 
    if (line.find("//") == 0) continue;

    DomainEntry entry;

    if (line.find("!") == 0)
    {
      entry.exception = true;

      line.erase(0, 1);
    }
    else if (line.find("*.") == 0)
    {
      entry.wildcard = true;

      line.erase(0, 2);
    }

    DomainSet::iterator it = domains.find(line);

    if (it != domains.end())
    {
      entry.Combine(it->second);

      domains.erase(it);
    }

    domains.insert(std::make_pair(line, entry));
  }

  return domains;
}

const std::string CUrl::GetDomain(void)
{
  const url_parse::Component& host = m_url.parsed_for_possibly_invalid_spec().host;

  if (host.len <= 0 || m_url.HostIsIPAddress())
    return std::string();
  
  return GetDomainAndRegistry(std::string(m_url.possibly_invalid_spec().data() + host.begin, host.len));
}

const std::string CUrl::GetDomainAndRegistry(const std::string& host) const
{
  size_t registry_length = GetRegistryLength(host);

  if (registry_length == std::string::npos || registry_length == 0)
    return std::string();

  // The "2" in this next line is 1 for the dot, plus a 1-char minimum preceding subcomponent length.
  assert(host.length() >= 2);

  if (registry_length > (host.length() - 2))   
    return std::string();

  // Move past the dot preceding the registry, and search for the next previous
  // dot.  Return the host from after that dot, or the whole host when there is
  // no dot.
  const size_t dot = host.rfind('.', host.length() - registry_length - 2);

  return dot == std::string::npos ? host : host.substr(dot + 1);
}

size_t CUrl::GetRegistryLength(const std::string& host) const
{
  static const DomainSet domains = LoadTldNames();

  // Skip leading dots.

  const size_t host_check_begin = host.find_first_not_of('.');

  if (host_check_begin == std::string::npos) return 0;

  // A single trailing dot isn't relevant in this determination, but does need
  // to be included in the final returned length.
  size_t host_check_len = host.length();

  if (host[host_check_len - 1] == '.') 
  {
    --host_check_len;

    assert(host_check_len > 0);  // If this weren't true, the host would be ".",

    // and we'd have already returned above.
    if (host[host_check_len - 1] == '.')
      return 0;  // Multiple trailing dots.
  }

  // Walk up the domain tree, most specific to least specific,
  // looking for matches at each level.
  size_t prev_start = std::string::npos;
  size_t curr_start = host_check_begin;
  size_t next_dot = host.find('.', curr_start);

  if (next_dot >= host_check_len)  // Catches std::string::npos as well.
    return 0;  // This can't have a registry + domain.

  while (true)
  {
    DomainSet::const_iterator it = domains.find(
      std::string(host.c_str() + curr_start, host_check_len - curr_start));

    if (it != domains.end())
    {
      if (it->second.wildcard && (prev_start != std::string::npos)) 
      {
        return (prev_start == host_check_begin) ? 0 : (host.length() - prev_start);
      }

      if (it->second.exception) 
      {
        if (next_dot == std::string::npos)
        {
          // If we get here, we had an exception rule with no dots (e.g.
          // "!foo").  This would only be valid if we had a corresponding
          // wildcard rule, which would have to be "*".  But we explicitly
          // disallow that case, so this kind of rule is invalid.
          
          return 0;
        }

        return host.length() - next_dot - 1;
      }

      // If curr_start == host_check_begin, then the host is the registry itself

      return (curr_start == host_check_begin) ? 0 : (host.length() - curr_start);
    }

    if (next_dot >= host_check_len)  // Catches std::string::npos as well.
      break;

    prev_start = curr_start;
    curr_start = next_dot + 1;
    next_dot = host.find('.', curr_start);
  }

  return host.length() - curr_start;
}