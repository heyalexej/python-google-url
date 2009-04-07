#!/usr/bin/env python
import sys

import unittest
import logging

import gurl

class TestUrl(unittest.TestCase):
    def testConstructor(self):
        self.assertEquals("http://www.google.com/", str(gurl.Url("http://www.google.com")))
        
        self.assertEquals("http://www.google.com/", str(gurl.Url(u"http://www.google.com")))
        
        url = gurl.Url("http://www.google.com")
        
        self.assertEquals(str(url), str(gurl.Url(url)))
        
    def testNonzeroAndEmpty(self):
        url = gurl.Url("http://www.google.com")
        
        self.assert_(url)
        self.assertFalse(url.empty())
        
        url = gurl.Url("invalid url")

        self.assertFalse(url)
        self.assert_(url.empty())
        
        url = gurl.Url()

        self.assertFalse(url)
        self.assert_(url.empty())
        
    def testResolve(self):
        url = gurl.Url("http://www.google.com/index.htm")
        
        self.assertEquals("http://www.google.com/ad.js", str(url.resolve("ad.js")))
        self.assertEquals("http://www.google.com/ad.js", str(url.resolve(u"ad.js")))
        
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

if __name__ == '__main__':
    if "-v" in sys.argv:
        level = logging.DEBUG
    else:
        level = logging.WARN
    
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
    
    unittest.main()