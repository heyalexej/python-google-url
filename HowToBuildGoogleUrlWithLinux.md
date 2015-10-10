# Introduction #

How to build Google URL library with Linux

# Details #

  1. Checkout the latest source from SVN
```
$svn checkout http://google-url.googlecode.com/svn/trunk/ googleurl
```
  1. Create a [SConstruct](http://code.google.com/p/python-google-url/source/browse/trunk/google-url/linux/src/SConstruct) file in the googleurl/src folder
```
env = Environment(CPPPATH=["..", "../../"], CPPFLAGS=["-fPIC"])

source = [str(file) for file in Glob('*.cc')]

for file in Glob('*test*.cc'):
  source.remove(str(file))

#env.SharedLibrary('googleurl', source)
env.StaticLibrary('googleurl', source)
```
  1. Modify string16.cc, logging.h and basictypes.h in googleurl/base folder for compatibility
```
// string16.cc:31
#include <string.h>

// string16.h:54
#include <cstdio>

// logging.h:10
#ifdef WIN32
#include <tchar.h>
#else
#define TCHAR char
#endif

// basictypes.h:9
typedef unsigned long long uint64;
```
  1. Install [SCons](http://www.scons.org/) and run the scons command in the googleurl/src folder
```
$cd googleurl/src
$scons 
```
  1. export a environment variable GOOGLE\_URL\_HOME point to the googleurl folder
```
$export GOOGLE_URL_HOME=<Your path>/googleurl
```
  1. build and install the python extension
```
$svn checkout http://python-google-url.googlecode.com/svn/trunk/ python-google-url
$cd python-google-url
$python setup.py build
$sudo python setup.py install
```
  1. try to use it
```
$python
Python 2.6.1 (r261:67515, Apr 12 2009, 03:51:25) 
[GCC 4.3.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import gurl
>>> u = gurl.Url('http://code.google.com/p/python-google-url/')
>>> str(u)
```