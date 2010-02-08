#pragma once

#ifdef _WIN32
# pragma warning( push )

# pragma warning( disable : 4100 ) // 'identifier' : unreferenced formal parameter
# pragma warning( disable : 4121 ) // 'symbol' : alignment of a member was sensitive to packing
# pragma warning( disable : 4244 ) // 'argument' : conversion from 'type1' to 'type2', possible loss of data
# pragma warning( disable : 4512 ) // 'class' : assignment operator could not be generated
#endif 

#include <map>
#include <string> 

#include <boost/python.hpp>
namespace py = boost::python;

#include <googleurl/src/gurl.h>

#ifdef _WIN32
# pragma comment( lib, "googleurl" )
# pragma comment( lib, "icuuc" )
#endif

#ifdef _WIN32
# pragma warning( pop )
#endif 

class CUrl
{
protected:
  GURL m_url;

  CUrl(const GURL& url)
    : m_url(url)
  {

  }
private:
  py::object convert(const std::string& value) const
  {
    return py::str(value.c_str());
  }
  py::object convert(PyObject *obj) const
  {
    return py::object(py::handle<>(obj));
  }
  template <typename T>
  py::object convert(T value) const
  {
    return py::object(value);
  }

  struct DomainEntry
  {
    bool exception;
    bool wildcard;

    DomainEntry()
      : exception(false), wildcard(false)
    {

    }

    void Combine(const DomainEntry& entry)
    {
      exception |= entry.exception;
      wildcard |=  entry.wildcard;
    }
  };

  typedef std::map<std::string, DomainEntry> DomainSet;

  static const DomainSet LoadTldNames(void);
  size_t GetRegistryLength(const std::string& host) const;
  const std::string GetDomainAndRegistry(const std::string& host) const;

  static const string16 to_string16(const std::wstring& str);
public:
  CUrl(void)
  {

  }

  CUrl(const std::string& url)
    : m_url(url)
  {

  }

  CUrl(const std::wstring& url)    
  {
    const string16 s = to_string16(url);
    GURL g(s);
    
    m_url.Swap(&g);
  }

  CUrl(const CUrl& other)
    : m_url(other.m_url)
  {

  }

  operator const GURL& () const
  {
    return m_url;
  }

  operator bool() const
  {
    return m_url.is_valid();
  }

  bool operator ==(const CUrl& obj) const
  {
    return m_url == obj.m_url;
  }

  bool operator !=(const CUrl& obj) const
  {
    return m_url != obj.m_url;
  }

  bool operator <(const CUrl& obj) const
  {
    return m_url < obj.m_url;
  }

  bool IsEmpty(void) const
  {
    return m_url.is_empty();
  }

  const CUrl ResolveA(const std::string& relative) const
  {
    return CUrl(m_url.Resolve(relative));
  }

  const CUrl ResolveW(const std::wstring& relative) const
  {
    return CUrl(m_url.Resolve(to_string16(relative)));
  }

  const std::string GetSpec(bool raw=false) { return raw ? m_url.possibly_invalid_spec() : m_url.spec(); }

  const std::string GetScheme(void) { return m_url.scheme(); }
  py::object GetUsername(void) { return m_url.has_username() ? convert(m_url.username()) : py::object(); }
  py::object GetPassword(void) { return m_url.has_password() ? convert(m_url.password()) : py::object(); }
  py::object GetHost(void) { return m_url.has_host() ? convert(m_url.host()) : py::object(); }
  py::object GetPort(void) { return m_url.has_port() ? convert(atoi(m_url.port().c_str())) : py::object(); }
  const std::string GetPath(void) { return m_url.path(); }
  const std::string GetQuery(void) { return m_url.query(); }
  const std::string GetRef(void) { return m_url.ref(); }

  const std::string GetFilename(void) { return m_url.ExtractFileName(); }
  const std::string GetDomain(void);
  bool IsStandard(void) { return m_url.IsStandard(); }

  const CUrl GetWithEmptyPath(void) { return CUrl(m_url.GetWithEmptyPath()); }
  const CUrl GetOrigin(void) { return CUrl(m_url.GetOrigin()); }
  bool HostIsIPAddress(void) { return m_url.HostIsIPAddress(); }
  const std::string PathForRequest(void) { return m_url.PathForRequest(); }

  bool SchemeIs(const std::string& scheme) { return m_url.SchemeIs(scheme.c_str()); }
  bool DomainIs(const std::string& domain) { return m_url.DomainIs(domain.c_str(), (int) domain.size()); }

  static void Expose(void);
};
