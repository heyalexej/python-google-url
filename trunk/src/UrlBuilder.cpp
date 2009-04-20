#include "UrlBuilder.h"

std::ostream& operator <<(std::ostream& os, const CUrlBuilder& builder)
{ 
  os << static_cast<const GURL&>(builder);

  return os;
}

void CUrlBuilder::Expose(void)
{
  py::class_<CUrlBuilder, py::bases<CUrl> >("UrlBuilder", py::init<>())
    .def(py::init<const std::string>())
    .def(py::init<const std::wstring>())
    .def(py::init<const CUrl>())

    .def(str(py::self))

    .add_property("scheme", &CUrlBuilder::GetScheme, &CUrlBuilder::SetScheme)
    .add_property("username", &CUrlBuilder::GetUsername, &CUrlBuilder::SetUsername)
    .add_property("password", &CUrlBuilder::GetPassword, &CUrlBuilder::SetPassword)
    .add_property("hostname", &CUrlBuilder::GetHost, &CUrlBuilder::SetHost)
    .add_property("port", &CUrlBuilder::GetPort, &CUrlBuilder::SetPort)
    .add_property("path", &CUrlBuilder::GetPath, &CUrlBuilder::SetPath)
    .add_property("query", &CUrlBuilder::GetQuery, &CUrlBuilder::SetQuery)
    .add_property("fragment", &CUrlBuilder::GetRef, &CUrlBuilder::SetRef)
    ;
}
