#include "Url.h"
#include "UrlBuilder.h"

BOOST_PYTHON_MODULE(_gurl)
{
  CUrl::Expose();
  CUrlBuilder::Expose();
}
