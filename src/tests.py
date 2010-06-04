#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import unittest
import logging

import gurl

class TestUrl(unittest.TestCase):
    def testConstructor(self):
        self.assertEquals("http://www.google.com/", str(gurl.Url("http://www.google.com")))
        
        self.assertEquals("http://www.google.com/", str(gurl.Url(u"http://www.google.com")))
        
        url = gurl.Url("http://www.google.com")
        
        self.assert_(url == gurl.Url(url))
        
    def testNonzeroAndEmpty(self):
        url = gurl.Url("http://www.google.com")
        
        self.assert_(url)
        self.assert_(url.isstandard())
        self.assertFalse(url.empty())
        self.assertEquals("http://www.google.com/", url.spec())
        
        url = gurl.Url("http://google.com:foo/")

        self.assertFalse(url)
        
        self.assertEquals("http://google.com:foo/", url.spec(raw=True))
        
        url = gurl.Url()

        self.assertFalse(url)
        self.assert_(url.empty())
        
    def testMethods(self):
        url = gurl.Url("http://www.google.com/index.htm")
        
        self.assert_(url.isstandard())
        
        self.assertEquals("http://www.google.com/ad.js", str(url.join("ad.js")))
        self.assertEquals("http://www.google.com/ad.js", str(url.join(u"ad.js")))
        
        self.assert_(url.schemeis("http"))
        
        self.assertFalse(url.schemeis("ftp"))
        self.assertFalse(url.schemeis("HTTP"))
        
        self.assert_(url.domainis("www.google.com"))
        self.assert_(url.domainis("google.com"))
        self.assert_(url.domainis("com"))
        
        self.assertFalse(url.domainis("WWW.google.com"))
        self.assertFalse(url.domainis("www.test.com"))
        
    def testProperties(self):
        url = gurl.Url("http://user:pass@www.google.com:8080/index.htm?id=1234#tag")
        
        self.assertEquals("http", url.scheme)
        self.assertEquals("user", url.username)
        self.assertEquals("pass", url.password)
        self.assertEquals("www.google.com", url.hostname)
        self.assertEquals(8080, url.port)
        self.assertEquals("/index.htm", url.path)
        self.assertEquals("id=1234", url.query)
        self.assertEquals("tag", url.fragment)
        
        self.assertEquals("index.htm", url.filename)
        
        self.assertEquals("http://user:pass@www.google.com:8080/", str(url.host))
        self.assertEquals("http://www.google.com:8080/", str(url.origin))
        self.assertFalse(url.hostisip)
        self.assert_(gurl.Url("http://127.0.0.1").hostisip)
        self.assertEquals("/index.htm?id=1234", url.request)
        
    def testOperators(self):
        self.assert_(gurl.Url("http://www.google.com") == gurl.Url("http://www.google.com"))
        self.assert_(gurl.Url("http://www.google.com") != gurl.Url("http://www.yahoo.com"))
        self.assert_(gurl.Url("http://www.google.com") < gurl.Url("http://www.yahoo.com"))
        
    def testDomain(self):
        self.assertEquals("google.com", gurl.Url("http://www.google.com").domain)
        self.assertEquals("google.com.cn", gurl.Url("http://www.google.com.cn").domain)
        self.assertEquals("xn--55qx5d.cn", gurl.Url(u"http://www.google.公司.cn").domain)
        
        self.assertEquals("google.edu.ar", gurl.Url("http://www.google.edu.ar").domain)
        self.assertEquals("uba.ar", gurl.Url("http://www.google.uba.ar").domain)

class TestUrlBuilder(unittest.TestCase):
    def testConstructor(self):
        self.assertEquals("http://www.google.com/", str(gurl.UrlBuilder("http://www.google.com")))
        
        self.assertEquals("http://www.google.com/", str(gurl.UrlBuilder(u"http://www.google.com")))
        
        url = gurl.Url("http://www.google.com")
        
        self.assert_(url == gurl.UrlBuilder(url))
        
    def testProperties(self):
        url = gurl.UrlBuilder("http://user:pass@www.google.com:8080/index.htm?id=1234#tag")
        
        url.scheme = "https"
        
        self.assertEquals("https", url.scheme)
        
        url.username = "who"
        
        self.assertEquals("who", url.username)
        
        url.password = "hello"
        
        self.assertEquals("hello", url.password)
        
        url.hostname = "www.microsoft.com"
        
        self.assertEquals("www.microsoft.com", url.hostname)
                
        url.port = 80
        
        self.assertEquals(80, url.port)
        
        url.path = "/test"
        
        self.assertEquals("/test", url.path)
        
        url.query = "name=flier"
        
        self.assertEquals("name=flier", url.query)
        
        url.fragment = "test"
        
        self.assertEquals("test", url.fragment)
        
        url.username = None
        url.password = None
        url.port = None
        url.path = None
        url.fragment = None
        
        self.assertEquals("https://www.microsoft.com/?name=flier", str(url))

if __name__ == '__main__':
    if "-v" in sys.argv:
        level = logging.DEBUG
    else:
        level = logging.WARN
    
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
    
    unittest.main()