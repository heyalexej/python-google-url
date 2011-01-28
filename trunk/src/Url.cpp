#include "Url.h"

#include <cassert>
#include <fstream> 

#ifndef WIN32
#include <unicode/ustring.h>
#endif

#include <boost/algorithm/string.hpp>

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
