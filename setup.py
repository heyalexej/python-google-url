#!/usr/bin/env python
import ez_setup

ez_setup.use_setuptools()

import sys, os, os.path, re, shutil
import subprocess

from setuptools import setup
from setuptools.extension import Extension
from distutils.command.build import build as _build

DEBUG = False

PYGURL_HOME = os.path.dirname(__file__)
BOOST_HOME = None
BOOST_PYTHON_MT = False
PYTHON_HOME = None
ICU_HOME = None
GOOGLE_URL_HOME = None
GOOGLE_URL_SVN = 'http://google-url.googlecode.com/svn/trunk'

# load defaults from config file
try:
    from buildconf import *
except ImportError:
    pass

BOOST_HOME = os.environ.get('BOOST_HOME', BOOST_HOME)
BOOST_PYTHON_MT = os.environ.get('BOOST_PYTHON_MT', BOOST_PYTHON_MT)
PYTHON_HOME = os.environ.get('PYTHON_HOME', PYTHON_HOME)
ICU_HOME = os.environ.get('ICU_HOME', ICU_HOME)
GOOGLE_URL_HOME = os.environ.get('GOOGLE_URL_HOME', GOOGLE_URL_HOME)

if GOOGLE_URL_HOME is None or not os.path.exists(os.path.join(GOOGLE_URL_HOME, 'src', 'gurl.h')):
    print "WARN: GOOGLE_URL_HOME doesn't exists or point to a wrong folder, ",
    print "      we will try to checkout and build a private build from <%s>." % GOOGLE_URL_SVN

    GOOGLE_URL_HOME = os.path.join(GOOGLE_URL_HOME, 'build', 'googleurl')
else:
    print "Found Google v8 base on GOOGLE_URL_HOME <%s>, update it to latest SVN trunk" % GOOGLE_URL_SVN

source_files = ["Url.cpp", "UrlBuilder.cpp", "gurl.cpp", "logging.cpp"]

libraries = ["googleurl"]
macros = [("BOOST_PYTHON_STATIC_LIB", None), ]
extra_compile_args = ["-DOMIT_DLOG_AND_DCHECK=1"]
extra_link_args = []

if os.name == "nt":
    macros += [("WIN32", None), ]
    include_dirs = [BOOST_HOME,
                    os.path.join(PYTHON_HOME, 'include'),
                    GOOGLE_URL_HOME,
                    os.path.join(GOOGLE_URL_HOME, '..')]
    library_dirs = [os.path.join(BOOST_HOME, 'stage', 'lib'),
                    os.path.join(PYTHON_HOME, 'libs'),
                    os.path.join(GOOGLE_URL_HOME, 'build', 'Debug' if DEBUG else 'Release'),
                    os.path.join(ICU_HOME, 'lib'), ]
    libraries += ["user32", "advapi32"]
    extra_compile_args += ["/O2", "/GL", "/MT", "/EHsc", "/Gy", "/Zi"]
    extra_link_args += ["/DLL", "/OPT:REF", "/OPT:ICF", "/MACHINE:X86", "/LTCG"]

    if ICU_HOME is None or not os.path.exists(os.path.join(ICU_HOME, 'lib', 'icuuc.lib')):
        print "WARN: ICU_HOME doesn't exists or point to a wrong folder, "
        print "      please download the latest ICU library from http://site.icu-project.org/download"

    for root, dirs, files in os.walk(os.path.join(ICU_HOME, 'bin')):
        for name in files:
            if re.compile('icu(uc|dt)\d+\.dll', re.I).match(name):
                shutil.copyfile(os.path.join(root, name),
                                os.path.join(os.path.dirname(__file__), "src", "gurl", name))
elif os.name == "posix":
    source_files += [os.path.join(GOOGLE_URL_HOME, 'base', 'string16.cc')]
    libraries += ["boost_python", "boost_system", "boost_filesystem", "rt", "icuuc", "icui18n"]
    include_dirs = [GOOGLE_URL_HOME,
                    os.path.join(GOOGLE_URL_HOME, '..')]
    library_dirs = [os.path.join(GOOGLE_URL_HOME, 'src'),
                    os.path.join(GOOGLE_URL_HOME, 'base'), ]

class build(_build):
    def checkout_googleurl(self):
        print "INFO: updating Google url to latest SVN trunk ..."
        
        if not os.path.isdir(GOOGLE_URL_HOME):
            os.makedirs(GOOGLE_URL_HOME)

            cmd = "co"
        else:
            cmd = "up"

        proc = subprocess.Popen(["svn", cmd, GOOGLE_URL_SVN, GOOGLE_URL_HOME],
                                stdout=sys.stdout, stderr=sys.stderr)

        proc.communicate()

        if proc.returncode != 0:
            print "WARN: fail to checkout or update Google v8 code from SVN, error code: ", proc.returncode

    def patch_googleurl(self):
        from patch import PatchSet

        print "INFO: patching Google url ... ",

        shutil.copyfile(os.path.join(PYGURL_HOME, 'google-url', 'linux', 'src', 'SConstruct'),
                        os.path.join(GOOGLE_URL_HOME, 'src', 'SConstruct'))

        cwd = os.getcwd()
        os.chdir(GOOGLE_URL_HOME)

        with open(os.path.join(PYGURL_HOME, 'google-url', 'linux', 'linux.patch')) as patchfile:
            patch = PatchSet(patchfile)
            ok = patch.apply()

            print "succeeded" if ok else "failed"

        os.chdir(cwd)

    def build_googleurl(self):
        print "INFO: building Google url with SCons ..."

        if os.name == "nt":
            proc = subprocess.Popen(["msbuild", "googleurl.sln", "/p:Configuration=%s" % ('Debug' if DEBUG else 'Release')],
                                    cwd=os.path.join(GOOGLE_URL_HOME, 'build'),
                                    shell=True, stdout=sys.stdout, stderr=sys.stderr)
        else:
            proc = subprocess.Popen(["scons"],
                                    cwd=os.path.join(GOOGLE_URL_HOME, 'src'),
                                    shell=True, stdout=sys.stdout, stderr=sys.stderr)

        proc.communicate()

        if proc.returncode != 0:
			print "WARN: fail to build Google url code from SVN, error code: ", proc.returncode

    def run(self):
        self.checkout_googleurl()
        self.patch_googleurl()
        self.build_googleurl()

        _build.run(self)

gurl_module = Extension(
        name="_gurl",
        sources=[os.path.join("src", file) for file in source_files],
        define_macros=macros,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        )

setup(
        name="python-google-url",
        version="0.5",
        cmdclass = { 'build': build },
        ext_package="gurl",
        ext_modules=[gurl_module],
        packages=["gurl"],
        package_dir={"gurl": os.path.join("src", "gurl")},
        package_data={"gurl": ["*.dat", "*.dll"]},

        # metadata for upload to PyPI
        author="Flier Lu",
        author_email="flier.lu@gmail.com",
        description="A python wrapper for google-url project",
        long_description="A small library for parsing and canonicalizing URLs.",
        license="New BSD",
        keywords="google url",
        url="http://code.google.com/p/python-google-url/",
        download_url="http://code.google.com/p/python-google-url/downloads/list",
        classifiers=[
                "Development Status :: 4 - Beta",
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