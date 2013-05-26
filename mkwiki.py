#!/usr/bin/env python
#
# mediawiki installation & customization tool
#
# reference docs:
#
# http://docs.python.org/2/library/array.html
# http://docs.python.org/2/library/re.html
# http://docs.python.org/2/library/subprocess.html
# http://docs.python.org/2/library/sqlite3.html
#
# 0.0.1
#       05:52 ??0313 first real working version!!!!
#
# 0.0.2
#       adding support for creation of CustomSettings.php file
#       three files will be supported initially:
#       * LocalSettings.php (add reference to CustomSettings.php)
#       * CustomSettings.php: actual configuration
#       * basic (working) .htaccess
#

import os
import sys
import stat as stat
import re
import subprocess
import array
import sqlite3

# will handle platform related configuration
# php, apache and sites home

class wikiPlatform:
    pass

# will handle extensions and their configuration
#

class wikiExtension:
    'extension management class'

    def __init__(self, name, init_file = None):

      if init_file is None:
         init_fullpath = 'extensions/' + name + '/' + name + '.php' 

#
#
class htaccess:

   destDir = None
   htaccessFile = None

   def __init__(self, wiki):
     if isinstance(wiki, mkwiki):
        destDir = wiki.destDir
        htaccessFile = destDir + '/.htaccess'

#
# handles custom configuratios
# LocalSettings.php will be left almost untouched apart from parameters we allow changing
# customsettings should be saved also in a binary file or in a database so to better
# handle automatic rebuild.. more details TBD
#
# This class might be removed as its features should be integrated with
# the mkwiki class
#

class customSettings:
     'manage custom settings'

     _customArray = []
     _arrayLength = 0

     customsettings = None

     localsettings = None
     id = None

     def __init__(self, wiki = None):
        if isinstance(wiki, mkwiki):
           self.localsettings = wiki.LocalSettings
           self.customsettings = wiki.destDir + "/" + "CustomSettings.php"
           self.id = wiki.id

        if isinstance(wiki, str) and os.path.exists(wiki):
           #workinprogress
           pass

     def add(self, line):
       'add a line to custom settings file'

       if line is not None:
	  self._customArray.append(line)

# load settings
     def load(self):
       try:
         fh = open (self.customsettings)
       except Exception as e:
	 # might be empty or does not exist, directory should exist, this will be tested
         _arrayLength = 0
         return

       for line in fh:
           line = line.strip()
	   self._customArray.append(line)

       _arrayLength = len(self._customArray)


     def show(self):
        '''show contents of customarray'''

        for line in self._customArray:
           print line
       

     def write(self):
        try:
          fh = open(self.customsettings, 'w');
        except Exception as e:
          print 'write: error for file: ' + self.customsettings
          print type(e)
          print e.args
	
          return

        for item in self._customArray:
          fh.write(item+'\n')

        fh.close()


# "master" wiki generation class

class mkwiki:
   'wiki creation class - naming convention to be reviewed!!!'

   version = '0.0.2'
   adminUser = 'admin'
   LocalSettings = None
   htaccessFile = None
   _htaccessArray = []
   destDir = None
   dbType = 'sqlite'
   wikiName = None
   installCmd = None
   phpSep = "/"

   def __init__(self, site_domain, site_id, full_url = None, wiki_name = None):

       if self.test_cygwin:
         self.is_cygwin = True
         self.phpSep = '\\' #this almost incorrect: shoul test if httpd is native or cygwin, we imply we are using my env!
       else:
	 self.is_cygwin = False

       self.id = site_id
       self.domain = site_domain

       if wiki_name is not None:
          self.wikiName = wiki_name
       else:
          self.wikiName = self.id

       self.setupAuth()

       #internal objects - dependant on system configuration/apache install/etc
       self.setupInternals()

       #database initializaton function
       self.setupDB()

       # wikiUrl 
       if full_url is None:
          self.wikiUrl = "http://" + self.domain 
       else:
          self.wikiUrl = full_url

       # scriptpath .. currently empty
       self.scriptpath = ""

       # API init
       self.setupAPI()

       # configuration files
       self.LocalSettings = self.destDir + "/" + "LocalSettings.php"

# authentication

   def setupAuth(self):
       '''setup default wiki username and password'''
       if self.adminUser is None:
         self.adminUser = 'admin'

       self.adminPass = self.id + "0x"


# internal configs - will be stored in a config file - sqlite or xml

   def setupInternals(self, _phpDir = None, _rootDir = None):
       '''setup for platform related variables'''
       #directory where php is installed: a way to dynamically configure this is needed
       if _phpDir is None:
          self.phpDir = "/c/apache/php5"
       else:
          self.phpDir = _phpDir

       # directory where all websites are

       if _rootDir is None:
          self.rootDir = "/c/apache/sites"
       else:
          self.rootDir = _phpDir
       # where all html will be located
       self.destDir = self.rootDir + "/" + self.id + "/" + "html"
       # rootDir/id/db/ - this will be used by native installer
       self.dataDir = self.rootDir + "/" + self.id + "/" + "db"

       #install.php
       self.phpFile= self.destDir + "/maintenance/install.php"

       ####
       #cygwin variables: phpFile & datPath
       # these must be changed to a windows format if using cygwin BUT Apache is Windows Native
       if self.is_cygwin:
	 self.dataDir = subprocess.check_output(["cygpath", "-w", self.dataDir]);
	 self.dataDir = self.dataDir.replace('\n','');
	 self.phpFile = subprocess.check_output(["cygpath", "-w", self.phpFile]);
	 self.phpFile = self.phpFile.replace('\n','');

       #php executable
       self.phpCmd = self.phpDir + "/" + "php"

# "temporary" function which handles all database init

   def setupDB(self):
       """
       setup DB variables & connection
       """
       # dbserver.. not really needed for sqlite
       #this should be moved to a platform configuration
       self.dbserver = "localhost"
       # dbname (will be filename for sqlite?)
       self.dbname = self.id + "_db"
       # full db pat - this is used internally, so no need to use cygpath if under cygwin
       self.fulldbpath = self.dataDir + self.phpSep + self.dbname + ".sqlite"

   def setupAPI(self):
       # API url
       if self.scriptpath is None or self.scriptpath == "":
          self.apiUrl = self.wikiUrl + '/api.php'
       else:
          self.apiUrl = self.wikiUrl + '/' + self.scriptpath + '/api.php'

# slightly different behaviour if we are using cygwin
# should be replace by using platform class

   def test_cygwin():
       uname = os.uname()[0];
       matchObj = re.search('cygwin', uname.lower(), flags=0);
       if matchObj:
         return True
       else:
         return False

# see content of created database
#sqlite> select page_id,page_namespace,page_is_new, page_title from page;
#1|0|1|Main_Page

   def testDB(self):
       dbConn = sqlite3.connect(self.fulldbpath) #warning should perform some tests..
       cur = dbConn.cursor()
       cur.execute ("select page_id,page_namespace,page_is_new, page_title from page");
       print cur.fetchone()

# prepares strings to be executed

   def prepareInstallCmd(self):
       self.installCmd = (self.phpCmd + ' "'   + self.phpFile    + '"' +
			  ' --dbpath="'        + self.dataDir    + '"' +
			  ' --dbtype="'        + self.dbType     + '"' +
			  ' --wiki="'          + self.id         + '"' +
			  ' --pass="'          + self.adminPass  + '"' +
			  ' --server="'        + self.wikiUrl    + '"' +
			  ' --dbname="'        + self.dbname     + '"' +
			  ' --scriptpath="'    + self.scriptpath + '"' +
			  ' --dbserver="'      + self.dbserver   + '"' +
			  ' ' + self.id + ' ' + self.adminUser
			)
       return
       
# load mkwiki configuration
   def run(self):
       #TBD: if installCmd is empty or not set should we return, try to "prepare" it or... ??
       if self.installCmd == "" or self.installCmd is None:
         return

       if os.path.exists(self.LocalSettings):
         print 'already installed: ' + self.domain
         return

       print "executing: " + self.installCmd
       subprocess.call(self.installCmd,shell=True);

       #subprocess.call(["chmod", "777", self.fulldbpath]);
       # sqlite "database" must be writeable by webserver
       if self.dbType == 'sqlite':
          os.chmod(self.fulldbpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IWOTH | stat.S_IROTH)

       return

# print LocalSettings
   def printSettings(self):
       fh = open (self.LocalSettings)
       confArray = []
       filtComments   = re.compile(r'^#')
       filtEmptyLines = re.compile(r'^$')
       for line in fh:
	   line = line.strip()
	   if filtComments.match(line) or filtEmptyLines.match(line):
	     continue
	   print line
           confArray.append(line)

       print ''
       print 'Length: ' + str(len(confArray))
       fh.close

# load settings
   def loadSettings(self):
       fh = open (self.LocalSettings)

       _confArray = []

       for line in fh:
           line = line.strip()
	   _confArray.append(line)

       confLen = len(_confArray)

       print _confArray[confLen-10:confLen]

       print 'number of lines in conf is: ' + str(len(_confArray))
  
# debug/info use only
 
   def printEnv(self):
       print "id             = " + self.id
       print "domain         = " + self.domain
       print "phpDir         = " + self.phpDir
       print "rootDir        = " + self.rootDir
       print "dataDir        = " + self.dataDir
       print "wikiUrl        = " + self.wikiUrl
       print "wikiName       = " + self.wikiName
       print "phpCmd         = " + self.phpCmd
       print "LocalSettings  = " + self.LocalSettings
       print "fulldbpath     = " + self.fulldbpath
       print "destDir        = " + str(self.destDir)
       print "phpFile        = " + str(self.phpFile)
       print "installCmd     = " + str(self.installCmd)
       print "adminUser      = " + str(self.adminUser)
       print "adminPass      = " + str(self.adminPass)
       print "dbserver       = " + str(self.dbserver)
       print "is_cygwin      = " + str(self.is_cygwin)
       return
   
   def htaccess(self, wikipath = 'w'):
       """
       create basic htaccess - TBC
       """
       return

# this is the function that will
   def readConfig(self, config="mkwiki.config"):
       dbConn = sqlite3.connect(config) #warning should perform some tests..
       cur = dbConn.cursor()
       #cur.execute ("select page_id,page_namespace,page_is_new, page_title from page");
       cur.execute ("select site_id from sites");
       return

## Test code for above classes ##


def main(argv=None):
   if argv is None:
      argv = sys.argv
 
   if len(argv) == 1:
      fqdn="b.20wiki.net"
      id="b_20wiki_net"
   else:
      if len(argv) == 2:
        fqdn = argv[1]
        id = fqdn.replace('.','_')
      else:
        fqdn = argv[1]
        id = argv[2]
 
   print 'Full Domain: ' + fqdn
   print 'Wiki ID: ' + id
   print 
 
   try:
     wi = mkwiki(fqdn, id, None, 'Test Wiki') # fqdn, wiki id, full url, wiki name
   except Exception as e:
     print e
     return
 
   wi.printEnv()
   wi.prepareInstallCmd()
 
   try:
     wi.run()
   except Exception as e:
     print e 
     return
 
   cs = customSettings(wi)
   cs.load()
   cs.add('#this is a test comment');
   cs.add('');
   cs.add('$wgArticlePath      = "/w/$1";');
   cs.write()
  
   print "filedest: " + cs.customsettings
   
   print type(wi)
  
   hta = htaccess(wi)
   print hta.htaccessFile
  
  
if __name__ == "__main__":
   sys.exit(main())
  


## EOF ##
