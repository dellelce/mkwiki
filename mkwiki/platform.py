#!/usr/bin/env python
#
# File:         platform.py
# Created:      0013 050713
# Description:  description for platform.py
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

    self.phpDir = "/c/apache/php5"
    self.rootDir = "/c/apache/sites"
    self.extension = 'php'   # this might change
    self.fileSep = '/'
    self.apacheFileSep = '\\' # some platforms (i.e cygwin) have multiple separators (i.e. native & non-native)

  def dump_json(self):
    '''returns current wikiPlatform configuration as a json string'''
 
    json_layout = { 'phpDir': self.phpDir, 'rootDir': self.rootDir, 'extension' : self.extension, 'fileSetp': self.fileSep, 'apacheFileSep': self.apacheFileSep }

    return json.dumps(json_layout, sort_keys=True, indent=2) 

  def read_from_json(self,jsonobj):
    '''reads platform configuration from json object'''
    pass

  def load_json(self, name):
 
    try:
      self.fh = open(name,'r')
    except Exception as e:
      return e

    self.json_buf = self.fh.read()
    return json.loads(self.json_buf)

## EOF ##

