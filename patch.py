""" Patch utility to apply unified diffs

    Brute-force line-by-line non-recursive parsing 

    Copyright (c) 2008-2011 anatoly techtonik
    Available under the terms of MIT license

    Project home: http://code.google.com/p/python-patch/


    $Id$
    $HeadURL$
"""

__author__ = "techtonik.rainforce.org"
__version__ = "1.11.02-dev"

import copy
import logging
import re
# cStringIO doesn't support unicode in 2.5
from StringIO import StringIO
import urllib2

from os.path import exists, isfile, abspath
from os import unlink


#------------------------------------------------
# Logging is controlled by "python_patch" logger

debugmode = False

logger = logging.getLogger("python_patch")
loghandler = logging.StreamHandler()
logger.addHandler(loghandler)

debug = logger.debug
info = logger.info
warning = logger.warning

#: disable library logging by default
logger.setLevel(logging.CRITICAL)

#------------------------------------------------

# constants for patch types

DIFF = PLAIN = "plain"
HG = MERCURIAL = "mercurial"
SVN = SUBVERSION = "svn"


def fromfile(filename):
  """ Parse patch file and return PatchSet() object
      XXX error reporting
  """
  debug("reading %s" % filename)
  fp = open(filename, "rb")
  patchset = PatchSet(fp)
  fp.close()
  return patchset


def fromstring(s):
  """ Parse text string and return PatchSet() object
  """
  return PatchSet( StringIO(s) )


def fromurl(url):
  """ Read patch from URL
  """
  return PatchSet( urllib2.urlopen(url) )


class Hunk(object):
  """ Parsed hunk data container (hunk starts with @@ -R +R @@) """

  def __init__(self):
    self.startsrc=None #: line count starts with 1
    self.linessrc=None
    self.starttgt=None
    self.linestgt=None
    self.invalid=False
    self.text=[]

#  def apply(self, estream):
#    """ write hunk data into enumerable stream
#        return strings one by one until hunk is
#        over
#
#        enumerable stream are tuples (lineno, line)
#        where lineno starts with 0
#    """
#    pass


class Patch(object):
  """ Patch for a single file """
  def __init__(self):
    self.source = None 
    self.target = None
    self.hunks = []
    self.hunkends = []
    self.header = ''


class PatchSet(object):

  def __init__(self, stream=None):
    self.name = None   # descriptive name of the PatchSet

    # list of Patch objects
    self.items = []

    #: patch type - one of constants
    self.type = None

    if stream:
      self.parse(stream)

  def __len__(self):
    return len(self.items)

  def parse(self, stream):
    """ parse unified diff
        return True on success
    """
    lineends = dict(lf=0, crlf=0, cr=0)
    nexthunkno = 0    #: even if index starts with 0 user messages number hunks from 1

    p = None
    hunk = None
    # hunkactual variable is used to calculate hunk lines for comparison
    hunkactual = dict(linessrc=None, linestgt=None)


    class wrapumerate(enumerate):
      """Enumerate wrapper that uses boolean end of stream status instead of
      StopIteration exception, and properties to access line information.
      """

      def __init__(self, *args, **kwargs):
        # we don't call parent, it is magically created by __new__ method

        self._exhausted = False
        self._lineno = False     # after end of stream equal to the num of lines
        self._line = False       # will be reset to False after end of stream

      def next(self):
        """Try to read the next line and return True if it is available,
           False if end of stream is reached."""
        if self._exhausted:
          return False

        try:
          self._lineno, self._line = super(wrapumerate, self).next()
        except StopIteration:
          self._exhausted = True
          self._line = False
          return False
        return True

      @property
      def is_empty(self):
        return self._exhausted

      @property
      def line(self):
        return self._line

      @property
      def lineno(self):
        return self._lineno

    # define states (possible file regions) that direct parse flow
    headscan  = True  # start with scanning header
    filenames = False # lines starting with --- and +++

    hunkhead = False  # @@ -R +R @@ sequence
    hunkbody = False  #
    hunkskip = False  # skipping invalid hunk mode

    hunkparsed = False # state after successfully parsed hunk

    # regexp to match start of hunk, used groups - 1,3,4,6
    re_hunk_start = re.compile("^@@ -(\d+)(,(\d+))? \+(\d+)(,(\d+))?")
    
    errors = 0
    # temp buffers for header and filenames info
    header = ''
    srcname = None
    tgtname = None

    # start of main cycle
    # each parsing block already has line available in fe.line
    fe = wrapumerate(stream)
    while fe.next():

      # -- deciders: these only switch state to decide who should process
      # --           line fetched at the start of this cycle
      if hunkparsed:
        hunkparsed = False
        if re_hunk_start.match(fe.line):
            hunkhead = True
        elif fe.line.startswith("--- "):
            filenames = True
        else:
            headscan = True
      # -- ------------------------------------

      # read out header
      if headscan:
        while not fe.is_empty and not fe.line.startswith("--- "):
            header += fe.line
            fe.next()
        if fe.is_empty:
            if p == None:
              errors += 1
              warning("warning: no patch data is found")
            else:
              info("%d unparsed bytes left at the end of stream" % len(header))
              # TODO check for \No new line at the end.. 
              # TODO test for unparsed bytes
              # otherwise error += 1
            # this is actually a loop exit
            continue

        headscan = False
        # switch to filenames state
        filenames = True

      line = fe.line
      lineno = fe.lineno


      # hunkskip and hunkbody code skipped until definition of hunkhead is parsed
      if hunkbody:
        # process line first
        if re.match(r"^[- \+\\]", line):
            # gather stats about line endings
            if line.endswith("\r\n"):
              p.hunkends["crlf"] += 1
            elif line.endswith("\n"):
              p.hunkends["lf"] += 1
            elif line.endswith("\r"):
              p.hunkends["cr"] += 1
              
            if line.startswith("-"):
              hunkactual["linessrc"] += 1
            elif line.startswith("+"):
              hunkactual["linestgt"] += 1
            elif not line.startswith("\\"):
              hunkactual["linessrc"] += 1
              hunkactual["linestgt"] += 1
            hunk.text.append(line)
            # todo: handle \ No newline cases
        else:
            warning("invalid hunk no.%d at %d for target file %s" % (nexthunkno, lineno+1, p.target))
            # add hunk status node
            hunk.invalid = True
            p.hunks.append(hunk)
            errors += 1
            # switch to hunkskip state
            hunkbody = False
            hunkskip = True

        # check exit conditions
        if hunkactual["linessrc"] > hunk.linessrc or hunkactual["linestgt"] > hunk.linestgt:
            warning("extra lines for hunk no.%d at %d for target %s" % (nexthunkno, lineno+1, p.target))
            # add hunk status node
            hunk.invalid = True
            p.hunks.append(hunk)
            errors += 1
            # switch to hunkskip state
            hunkbody = False
            hunkskip = True
        elif hunk.linessrc == hunkactual["linessrc"] and hunk.linestgt == hunkactual["linestgt"]:
            # hunk parsed successfully
            p.hunks.append(hunk)
            # switch to hunkparsed state
            hunkbody = False
            hunkparsed = True

            # detect mixed window/unix line ends
            ends = p.hunkends
            if ((ends["cr"]!=0) + (ends["crlf"]!=0) + (ends["lf"]!=0)) > 1:
              warning("inconsistent line ends in patch hunks for %s" % p.source)
            if debugmode:
              debuglines = dict(ends)
              debuglines.update(file=p.target, hunk=nexthunkno)
              debug("crlf: %(crlf)d  lf: %(lf)d  cr: %(cr)d\t - file: %(file)s hunk: %(hunk)d" % debuglines)
            # fetch next line
            continue

      if hunkskip:
        if re_hunk_start.match(line):
          # switch to hunkhead state
          hunkskip = False
          hunkhead = True
        elif line.startswith("--- "):
          # switch to filenames state
          hunkskip = False
          filenames = True
          if debugmode and len(self.items) > 0:
            debug("- %2d hunks for %s" % (len(p.hunks), p.source))

      if filenames:
        if line.startswith("--- "):
          if srcname != None:
            # XXX testcase
            warning("skipping false patch for %s" % srcname)
            srcname = None
            # XXX header += srcname
            # double source filename line is encountered
            # attempt to restart from this second line
          re_filename = "^--- ([^\t]+)"
          match = re.match(re_filename, line)
          # todo: support spaces in filenames
          if match:
            srcname = match.group(1).strip()
          else:
            warning("skipping invalid filename at line %d" % lineno)
            errors += 1
            # XXX p.header += line
            # switch back to headscan state
            filenames = False
            headscan = True
        elif not line.startswith("+++ "):
          if srcname != None:
            warning("skipping invalid patch with no target for %s" % srcname)
            errors += 1
            srcname = None
            # XXX header += srcname
            # XXX header += line
          else:
            # this should be unreachable
            warning("skipping invalid target patch")
          filenames = False
          headscan = True
        else:
          if tgtname != None:
            # XXX seems to be a dead branch  
            warning("skipping invalid patch - double target at line %d" % lineno)
            errors += 1
            srcname = None
            tgtname = None
            # XXX header += srcname
            # XXX header += tgtname
            # XXX header += line
            # double target filename line is encountered
            # switch back to headscan state
            filenames = False
            headscan = True
          else:
            re_filename = "^\+\+\+ ([^\t]+)"
            match = re.match(re_filename, line)
            if not match:
              warning("skipping invalid patch - no target filename at line %d" % lineno)
              errors += 1
              srcname = None
              # switch back to headscan state
              filenames = False
              headscan = True
            else:
              if p: # for the first run p is None
                self.items.append(p)
              p = Patch()
              p.source = srcname
              srcname = None
              p.target = match.group(1).strip()
              p.header = header
              header = ''
              # switch to hunkhead state
              filenames = False
              hunkhead = True
              nexthunkno = 0
              p.hunkends = lineends.copy()
              continue

      if hunkhead:
        match = re.match("^@@ -(\d+)(,(\d+))? \+(\d+)(,(\d+))?", line)
        if not match:
          if not p.hunks:
            warning("skipping invalid patch with no hunks for file %s" % p.source)
            errors += 1
            # XXX review switch
            # switch to headscan state
            hunkhead = False
            headscan = True
            continue
          else:
            # TODO review condition case
            # switch to headscan state
            hunkhead = False
            headscan = True
        else:
          hunk = Hunk()
          hunk.startsrc = int(match.group(1))
          hunk.linessrc = 1
          if match.group(3): hunk.linessrc = int(match.group(3))
          hunk.starttgt = int(match.group(4))
          hunk.linestgt = 1
          if match.group(6): hunk.linestgt = int(match.group(6))
          hunk.invalid = False
          hunk.text = []

          hunkactual["linessrc"] = hunkactual["linestgt"] = 0

          # switch to hunkbody state
          hunkhead = False
          hunkbody = True
          nexthunkno += 1
          continue


    self.items.append(p)

    if not hunkparsed:
      if hunkskip:
        warning("warning: finished with warnings, some hunks may be invalid")
      elif headscan:
        if len(self.items) == 0:
          warning("error: no patch data found!")
          # ? sys.exit(-1)
        else: # extra data at the end of file
          pass 
      else:
        warning("error: patch stream is incomplete!")
        errors += 1

    if debugmode and len(self.items) > 0:
        debug("- %2d hunks for %s" % (len(p.hunks), p.source))

    # XXX fix total hunks calculation
    debug("total files: %d  total hunks: %d" % (len(self.items),
        sum(len(p.hunks) for p in self.items)))
    
    return (errors == 0)


  def apply(self):
    """ apply parsed patch
        return True on success
    """

    total = len(self.items)
    errors = 0
    #for fileno, filename in enumerate(self.source):
    for i,p in enumerate(self.items):

      f2patch = p.source
      if not exists(f2patch):
        f2patch = p.target
        if not exists(f2patch):
          warning("source/target file does not exist\n--- %s\n+++ %s" % (p.source, f2patch))
          errors += 1
          continue
      if not isfile(f2patch):
        warning("not a file - %s" % f2patch)
        errors += 1
        continue
      filename = f2patch

      debug("processing %d/%d:\t %s" % (i+1, total, filename))

      # validate before patching
      f2fp = open(filename)
      hunkno = 0
      hunk = p.hunks[hunkno]
      hunkfind = []
      hunkreplace = []
      validhunks = 0
      canpatch = False
      for lineno, line in enumerate(f2fp):
        if lineno+1 < hunk.startsrc:
          continue
        elif lineno+1 == hunk.startsrc:
          hunkfind = [x[1:].rstrip("\r\n") for x in hunk.text if x[0] in " -"]
          hunkreplace = [x[1:].rstrip("\r\n") for x in hunk.text if x[0] in " +"]
          #pprint(hunkreplace)
          hunklineno = 0

          # todo \ No newline at end of file

        # check hunks in source file
        if lineno+1 < hunk.startsrc+len(hunkfind)-1:
          if line.rstrip("\r\n") == hunkfind[hunklineno]:
            hunklineno+=1
          else:
            info("file %d/%d:\t %s" % (i+1, total, filename))
            info(" hunk no.%d doesn't match source file at line %d" % (hunkno+1, lineno))
            info("  expected: %s" % hunkfind[hunklineno])
            info("  actual  : %s" % line.rstrip("\r\n"))
            # not counting this as error, because file may already be patched.
            # check if file is already patched is done after the number of
            # invalid hunks if found
            # TODO: check hunks against source/target file in one pass
            #   API - check(stream, srchunks, tgthunks)
            #           return tuple (srcerrs, tgterrs)

            # continue to check other hunks for completeness
            hunkno += 1
            if hunkno < len(p.hunks):
              hunk = p.hunks[hunkno]
              continue
            else:
              break

        # check if processed line is the last line
        if lineno+1 == hunk.startsrc+len(hunkfind)-1:
          debug(" hunk no.%d for file %s  -- is ready to be patched" % (hunkno+1, filename))
          hunkno+=1
          validhunks+=1
          if hunkno < len(p.hunks):
            hunk = p.hunks[hunkno]
          else:
            if validhunks == len(p.hunks):
              # patch file
              canpatch = True
              break
      else:
        if hunkno < len(p.hunks):
          warning("premature end of source file %s at hunk %d" % (filename, hunkno+1))
          errors += 1

      f2fp.close()

      if validhunks < len(p.hunks):
        if self._match_file_hunks(filename, p.hunks):
          warning("already patched  %s" % filename)
        else:
          warning("source file is different - %s" % filename)
          errors += 1
      if canpatch:
        backupname = filename+".orig"
        if exists(backupname):
          warning("can't backup original file to %s - aborting" % backupname)
        else:
          import shutil
          shutil.move(filename, backupname)
          if self.write_hunks(backupname, filename, p.hunks):
            info("successfully patched %d/%d:\t %s" % (i+1, total, filename))
            unlink(backupname)
          else:
            errors += 1
            warning("error patching file %s" % filename)
            shutil.copy(filename, filename+".invalid")
            warning("invalid version is saved to %s" % filename+".invalid")
            # todo: proper rejects
            shutil.move(backupname, filename)

    # todo: check for premature eof
    return (errors == 0)


  def can_patch(self, filename):
    """ Check if specified filename can be patched. Returns None if file can
    not be found among source filenames. False if patch can not be applied
    clearly. True otherwise.

    :returns: True, False or None
    """
    filename = abspath(filename)
    for p in self.items:
      if filename == abspath(p.source):
        return self._match_file_hunks(filename, p.hunks)
    return None


  def _match_file_hunks(self, filepath, hunks):
    matched = True
    fp = open(abspath(filepath))

    class NoMatch(Exception):
      pass

    lineno = 1
    line = fp.readline()
    hno = None
    try:
      for hno, h in enumerate(hunks):
        # skip to first line of the hunk
        while lineno < h.starttgt:
          if not len(line): # eof
            debug("check failed - premature eof before hunk: %d" % (hno+1))
            raise NoMatch
          line = fp.readline()
          lineno += 1
        for hline in h.text:
          if hline.startswith("-"):
            continue
          if not len(line):
            debug("check failed - premature eof on hunk: %d" % (hno+1))
            # todo: \ No newline at the end of file
            raise NoMatch
          if line.rstrip("\r\n") != hline[1:].rstrip("\r\n"):
            debug("file is not patched - failed hunk: %d" % (hno+1))
            raise NoMatch
          line = fp.readline()
          lineno += 1

    except NoMatch:
      matched = False
      # todo: display failed hunk, i.e. expected/found

    fp.close()
    return matched


  def patch_stream(self, instream, hunks):
    """ Generator that yields stream patched with hunks iterable
    
        Converts lineends in hunk lines to the best suitable format
        autodetected from input
    """

    # todo: At the moment substituted lineends may not be the same
    #       at the start and at the end of patching. Also issue a
    #       warning/throw about mixed lineends (is it really needed?)

    hunks = iter(hunks)

    srclineno = 1

    lineends = {'\n':0, '\r\n':0, '\r':0}
    def get_line():
      """
      local utility function - return line from source stream
      collecting line end statistics on the way
      """
      line = instream.readline()
        # 'U' mode works only with text files
      if line.endswith("\r\n"):
        lineends["\r\n"] += 1
      elif line.endswith("\n"):
        lineends["\n"] += 1
      elif line.endswith("\r"):
        lineends["\r"] += 1
      return line

    for hno, h in enumerate(hunks):
      debug("hunk %d" % (hno+1))
      # skip to line just before hunk starts
      while srclineno < h.startsrc:
        yield get_line()
        srclineno += 1

      for hline in h.text:
        # todo: check \ No newline at the end of file
        if hline.startswith("-") or hline.startswith("\\"):
          get_line()
          srclineno += 1
          continue
        else:
          if not hline.startswith("+"):
            get_line()
            srclineno += 1
          line2write = hline[1:]
          # detect if line ends are consistent in source file
          if sum([bool(lineends[x]) for x in lineends]) == 1:
            newline = [x for x in lineends if lineends[x] != 0][0]
            yield line2write.rstrip("\r\n")+newline
          else: # newlines are mixed
            yield line2write
     
    for line in instream:
      yield line


  def write_hunks(self, srcname, tgtname, hunks):
    src = open(srcname, "rb")
    tgt = open(tgtname, "wb")

    debug("processing target file %s" % tgtname)

    tgt.writelines(self.patch_stream(src, hunks))

    tgt.close()
    src.close()
    return True



if __name__ == "__main__":
  from optparse import OptionParser
  from os.path import exists
  import sys

  opt = OptionParser(usage="1. %prog [options] unipatch-file\n"
                    "       2. %prog [options] http://host/patch",
                     version="python-patch %s" % __version__)
  opt.add_option("-q", "--quiet", action="store_const", dest="verbosity",
                                  const=0, help="print only warnings and errors", default=1)
  opt.add_option("-v", "--verbose", action="store_const", dest="verbosity",
                                  const=2, help="be verbose")
  opt.add_option("--debug", action="store_true", dest="debugmode", help="debug mode")
  (options, args) = opt.parse_args()

  if not args:
    opt.print_version()
    opt.print_help()
    sys.exit()
  debugmode = options.debugmode

  verbosity_levels = {0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}
  loglevel = verbosity_levels[options.verbosity]
  logformat = "%(message)s"
  if debugmode:
    loglevel = logging.DEBUG
    logformat = "%(levelname)8s %(message)s"
  logger.setLevel(loglevel)
  loghandler.setFormatter(logging.Formatter(logformat))


  patchfile = args[0]
  urltest = patchfile.split(':')[0]
  if (':' in patchfile and urltest.isalpha()
      and len(urltest) > 1): # one char before : is a windows drive letter
    patch = fromurl(patchfile)
  else:
    if not exists(patchfile) or not isfile(patchfile):
      sys.exit("patch file does not exist - %s" % patchfile)
    patch = fromfile(patchfile)

  #pprint(patch)
  patch.apply() or sys.exit(-1)

  # todo: document and test line ends handling logic - patch.py detects proper line-endings
  #       for inserted hunks and issues a warning if patched file has incosistent line ends
