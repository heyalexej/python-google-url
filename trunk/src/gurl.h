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

  bool empty(void) const
  {
    return m_url.is_empty();
  }
};