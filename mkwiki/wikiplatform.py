#!/usr/bin/env python
#
# File:         wikiplatform.py
# Created:      0013 050713
# Description:  interface to platform
#               renamed wikiplatform for python3 compatibility
#
#

import json
import os

# will handle platform related configuration
# php, apache and sites home

class wikiPlatform(object):
  '''handles everything platform specific'''

# initially static (we might handle multiple platforms
  def __init__(self, name = None):
    '''load specific platform information'''

    if name is None:
      self.defaults()
    else
      #read defaults from specified object

# defaults
  def defaults(self):
    '''sets platform defaults'''

    self.phpPath = "/c/apache/php5"
    self.rootDir = "/c/apache/sites"
    #custom site directory below rootDir
    self.siteDir = ""
    self.extension = 'php'   # this might change
    self.fileSep = '/'
    self.apacheFileSep = '\\' # some platforms (i.e cygwin) have multiple separators (i.e. native & non-native)

  ## dump_json
  def dump_json(self):
    '''returns current wikiPlatform configuration as a json string'''
 
    json_layout = { 'phpPath': self.phpPath, 'rootDir': self.rootDir, 'siteDir': self.siteDir, 'extension' : self.extension, 'fileSetp': self.fileSep, 'apacheFileSep': self.apacheFileSep }

    return json.dumps(json_layout, sort_keys=True, indent=2) 

  # read_from_json: it's actually a 'dictionary'
  # it is not 
  def read_from_json(self,jsonobj):
    '''reads platform configuration from json object'''
    pass

## load_json
  def load_json(self, name):
    '''load json variable from file''' 

    try:
      self.fh = open(name,'r')
    except Exception as e:
      return e

    self.json_buf = self.fh.read()
    return json.loads(self.json_buf)

## EOF ##

