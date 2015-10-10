A small library for parsing and canonicalizing URLs.

You could use it to parse URL with [CUrl](http://code.google.com/p/python-google-url/source/browse/trunk/src/Url.h) like [urlparse.urlunparse](http://pydoc.org/2.5.1/urlparse.html)

```
>>> import gurl
>>> url = gurl.Url("http://user:pass@www.google.com:8080/index.htm?id=1234#tag")
>>> print url.scheme
http
>>> print url.username
user
>>> print url.password
pass
>>> print url.hostname
www.google.com
>>> print url.port
8080
>>> print url.path
/index.htm
>>> print url.query
id=1234
>>> print url.fragment
tag
>>> print url.filename
index.htm
>>> print url.host
http://user:pass@www.google.com:8080/
>>> print url.origin
http://www.google.com:8080/
>>> print url.hostisip
False
>>> print url.request
/index.htm?id=1234
>>> print url
http://user:pass@www.google.com:8080/index.htm?id=1234#tag  
```

or replace some components of a immutability URL with [UrlBuilder](http://code.google.com/p/python-google-url/source/browse/trunk/src/UrlBuilder.h)

```
>>> url = gurl.UrlBuilder(url)
>>> url.scheme = "https"
>>> url.port = 8443
>>> url.username = None
>>> url.password = None
>>> print url
https://www.google.com:8443/index.htm?id=1234#tag
```

Please check [the unit test](http://code.google.com/p/python-google-url/source/browse/trunk/src/tests.py) for more detail.

The most power feature of google-url is the compatibility, please check [its unit test](http://code.google.com/p/google-url/source/browse/trunk/src/url_parse_unittest.cc) for more detail.