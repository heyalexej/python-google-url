#include "gurl.h"

std::ostream& operator <<(std::ostream& os, const CUrlWrapper& wrapper)
{ 
  os << static_cast<const GURL&>(wrapper);

  return os;
}

BOOST_PYTHON_MODULE(gurl)
{
  py::class_<CUrlWrapper>("Url", py::init<>())
    .def(py::init<const std::string>())
    .def(py::init<const std::wstring>())
    .def(py::init<const CUrlWrapper>())

    .def(str(py::self))

    .def("__nonzero__", &CUrlWrapper::operator bool)

    .def("empty", &CUrlWrapper::IsEmpty)

    .def("resolve", &CUrlWrapper::ResolveA)
    .def("resolve", &CUrlWrapper::ResolveW)

    .def_readonly("scheme", &CUrlWrapper::GetScheme)
    .def_readonly("username", &CUrlWrapper::GetUsername)
    .def_readonly("password", &CUrlWrapper::GetPassword)
    .def_readonly("hostname", &CUrlWrapper::GetHost)
    .def_readonly("port", &CUrlWrapper::GetPort)
    .def_readonly("path", &CUrlWrapper::GetPath)
    .def_readonly("query", &CUrlWrapper::GetQuery)
    .def_readonly("fragment", &CUrlWrapper::GetRef)
    ;
}