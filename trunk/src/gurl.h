#pragma once

#ifdef _WIN32
# pragma warning( push )

# pragma warning( disable : 4100 ) // 'identifier' : unreferenced formal parameter
# pragma warning( disable : 4121 ) // 'symbol' : alignment of a member was sensitive to packing
# pragma warning( disable : 4244 ) // 'argument' : conversion from 'type1' to 'type2', possible loss of data
# pragma warning( disable : 4512 ) // 'class' : assignment operator could not be generated
#endif 

#include <boost/python.hpp>
namespace py = boost::python;

#include <googleurl/src/gurl.h>

#ifdef _WIN32
# pragma comment( lib, "base" )
# pragma comment( lib, "googleurl" )
# pragma comment( lib, "icuuc" )
#endif

#ifdef _WIN32
# pragma warning( pop )
#endif 

class CUrlWrapper
{
  GURL m_url;

  CUrlWrapper(const GURL& url)
    : m_url(url)
  {

  }

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
public:
  CUrlWrapper(void)
  {

  }

  CUrlWrapper(const std::string& url)
    : m_url(url)
  {

  }

  CUrlWrapper(const std::wstring& url)
    : m_url(url)
  {

  }

  CUrlWrapper(const CUrlWrapper& wrapper)
    : m_url(wrapper.m_url)
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

  bool IsEmpty(void) const
  {
    return m_url.is_empty();
  }

  const CUrlWrapper ResolveA(const std::string& relative) const
  {
    return CUrlWrapper(m_url.Resolve(relative));
  }

  const CUrlWrapper ResolveW(const std::wstring& relative) const
  {
    return CUrlWrapper(m_url.Resolve(relative));
  }

  const std::string GetScheme(void) { return m_url.scheme(); }
  py::object GetUsername(void) { return m_url.has_username() ? convert(m_url.username()) : py::object(py::handle<>(Py_None)); }
  py::object GetPassword(void) { return m_url.has_password() ? convert(m_url.password()) : py::object(py::handle<>(Py_None)); }
  py::object GetHost(void) { return m_url.has_host() ? convert(m_url.host()) : py::object(py::handle<>(Py_None)); }
  py::object GetPort(void) { return m_url.has_port() ? convert(atoi(m_url.port().c_str())) : py::object(py::handle<>(Py_None)); }
  const std::string GetPath(void) { return m_url.path(); }
  const std::string GetQuery(void) { return m_url.query(); }
  const std::string GetRef(void) { return m_url.ref(); }

  const std::string GetFilename(void) { return m_url.ExtractFileName(); }

  bool DomainIs(const std::string& domain) { return m_url.DomainIs(domain.c_str(), domain.size()); }
};