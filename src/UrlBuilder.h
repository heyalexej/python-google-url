#pragma once

#include "Url.h"

class CUrlBuilder : public CUrl
{
  template <typename S, typename C>
  void SetProperty(S setter, C clearer, py::object value)
  {
    GURL::Replacements replacements;

    const char *str = NULL;
    char buf[65];

    if (value.ptr() == Py_None)
    {
      (replacements.*clearer)(); 
    }
    else if (PyInt_Check(value.ptr()))
    {
      str = _ltoa(PyInt_AS_LONG(value.ptr()), buf, 10);
    }
    else if (PyString_Check(value.ptr()))
    {
      str = PyString_AS_STRING(value.ptr());
    }
    else 
    {
      str = py::extract<const char *>(value)();
    }

    if (str)
      (replacements.*setter)(str, url_parse::Component(0, (int) strlen(str)));

    m_url = m_url.ReplaceComponents(replacements);
  }
public:
  CUrlBuilder(void)
  {

  }

  CUrlBuilder(const std::string& url)
    : CUrl(url)
  {

  }

  CUrlBuilder(const std::wstring& url)
    : CUrl(url)
  {

  }

  CUrlBuilder(const CUrl& url)
    : CUrl(url)
  {

  }

  void SetScheme(const std::string& scheme)
  {
    GURL::Replacements replacements;
    
    replacements.SetScheme(scheme.c_str(), url_parse::Component(0, (int) scheme.size()));

    m_url = m_url.ReplaceComponents(replacements);
  }

  void SetUsername(py::object value)
  {
    SetProperty(&GURL::Replacements::SetUsername, &GURL::Replacements::ClearUsername, value);
  }

  void SetPassword(py::object value)
  {
    SetProperty(&GURL::Replacements::SetPassword, &GURL::Replacements::ClearPassword, value);
  }

  void SetHost(py::object value)
  {
    SetProperty(&GURL::Replacements::SetHost, &GURL::Replacements::ClearHost, value);
  }

  void SetPort(py::object value)
  {
    SetProperty(&GURL::Replacements::SetPort, &GURL::Replacements::ClearPort, value);
  }

  void SetPath(py::object value)
  {
    SetProperty(&GURL::Replacements::SetPath, &GURL::Replacements::ClearPath, value);
  }

  void SetQuery(py::object value)
  {
    SetProperty(&GURL::Replacements::SetQuery, &GURL::Replacements::ClearQuery, value);
  }

  void SetRef(py::object value)
  {
    SetProperty(&GURL::Replacements::SetRef, &GURL::Replacements::ClearRef, value);
  }

  static void Expose(void);
};
