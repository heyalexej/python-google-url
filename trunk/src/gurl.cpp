#include "Url.h"
#include "UrlBuilder.h"

BOOST_PYTHON_MODULE(gurl)
{
  CUrl::Expose();
  CUrlBuilder::Expose();
}
