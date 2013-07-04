#!/usr/bin/env python
#
# File:         platform.py
# Created:      0013 050713
# Description:  description for platform.py
#
#

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
    self.apacheFileSep = '\/' # some platforms (i.e cygwin) have multiple separators (i.e. native & non-native)



## EOF ##

