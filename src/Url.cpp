#include "Url.h"

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

    .def_readonly("scheme", &CUrl::GetScheme)
    .def_readonly("username", &CUrl::GetUsername)
    .def_readonly("password", &CUrl::GetPassword)
    .def_readonly("hostname", &CUrl::GetHost)
    .def_readonly("port", &CUrl::GetPort)
    .def_readonly("path", &CUrl::GetPath)
    .def_readonly("query", &CUrl::GetQuery)
    .def_readonly("fragment", &CUrl::GetRef)

    .def_readonly("filename", &CUrl::GetFilename)    

    .def("schemeis", &CUrl::SchemeIs)
    .def("domainis", &CUrl::DomainIs)

    .def_readonly("host", &CUrl::GetWithEmptyPath)
    .def_readonly("origin", &CUrl::GetOrigin)
    .def_readonly("hostisip", &CUrl::HostIsIPAddress)
    .def_readonly("request", &CUrl::PathForRequest)
    ;
}
