#!/usr/bin/env python

import os

from setuptools import setup, find_packages
from setuptools.extension import Extension

source_files = ["Url.cpp", "UrlBuilder.cpp", "gurl.cpp", "logging.cpp",
                os.path.join(os.environ['GOOGLE_URL_HOME'], 'base', 'string16.cc')]

libraries = ["googleurl"]
macros = [("BOOST_PYTHON_STATIC_LIB", None), ]
extra_compile_args = ["-DOMIT_DLOG_AND_DCHECK=1"]
extra_link_args = []

if os.name == "nt":
    macros += [("WIN32", None), ]
    include_dirs = [os.environ['BOOST_HOME'],
                    os.path.join(os.environ['PYTHON_HOME'], 'include'),
                    os.environ['GOOGLE_URL_HOME'],
                    os.path.join(os.environ['GOOGLE_URL_HOME'], '..')]
    library_dirs = [os.path.join(os.environ['BOOST_HOME'], 'stage', 'lib'),
                    os.path.join(os.environ['PYTHON_HOME'], 'libs'),
                    os.path.join(os.environ['GOOGLE_URL_HOME'], 'build', 'Release'),
                    os.path.join(os.environ['ICU_HOME'], 'Release', 'lib'),]
    libraries += ["user32", "advapi32"]
    extra_compile_args += ["/O2", "/GL", "/MT", "/EHsc", "/Gy", "/Zi"]
    extra_link_args += ["/DLL", "/OPT:REF", "/OPT:ICF", "/MACHINE:X86", "/LTCG"]
elif os.name == "posix":
    source_files += ["logging.cpp"]
    libraries += ["boost_python", "boost_system", "boost_filesystem", "base", "rt", "icuuc", "icui18n"]
    include_dirs = [os.environ['GOOGLE_URL_HOME'],
                    os.path.join(os.environ['GOOGLE_URL_HOME'], '..')]
    library_dirs = [os.path.join(os.environ['GOOGLE_URL_HOME'], 'src'),
                    os.path.join(os.environ['GOOGLE_URL_HOME'], 'base'),]

gurl_module = Extension(
    name = "gurl",
    sources = [os.path.join("src", file) for file in source_files],
    define_macros = macros,
    include_dirs = include_dirs,
    library_dirs = library_dirs,
    libraries = libraries,
    extra_compile_args = extra_compile_args,
    extra_link_args = extra_link_args,
)

setup(
    name = "python-google-url",
    version = "0.3",
    ext_modules = [gurl_module],
    pakcages = find_packages("src"),
    package_dir = { "" : "src" },
    test_suite = "tests",
    
    # metadata for upload to PyPI
    author = "Flier Lu",
    author_email = "flier.lu@gmail.com",
    description = "A python wrapper for google-url project",
    long_description = "A small library for parsing and canonicalizing URLs.",
    license = "New BSD",
    keywords = "google url",
    url = "http://code.google.com/p/python-google-url/",
    download_url = "http://code.google.com/p/python-google-url/downloads/list",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities", 
    ],
    platforms="x86",
)