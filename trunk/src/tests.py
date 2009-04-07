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
        
    def testProperties(self):
        url = gurl.Url("http://www.google.com")
        
        self.assert_(url)
        self.assertFalse(url.empty())
        
        url = gurl.Url("invalid url")

        self.assertFalse(url)
        self.assert_(url.empty())
        
        url = gurl.Url()

        self.assertFalse(url)
        self.assert_(url.empty())

if __name__ == '__main__':
    if "-v" in sys.argv:
        level = logging.DEBUG
    else:
        level = logging.WARN
    
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
    
    unittest.main()