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
import stat
import re
import subprocess
import array
import sqlite3

# local import

import wikiplatform

# NEW, generic settings class
#

class settings(object):
   '''generic configuration file manager class'''

   def __str__(self):
      return self.fileName

   def __del__(self):
       if self.fileHandle is not None:
         self.fileHandle.close()
         del self.fileHandle

   def __radd__(self,other):

      if self.fileName is None:
         fnStr = ''
      else:
         fnStr = self.fileName

      return str(other) + fnStr

   def __init__(self,name = None):
      '''load settings file is name is net'''

      self.fileName = None
      self.fileArray = []
      self.fileHandle = None
      self.fileLength = 0
      self.lastException = None

      if name is not None:
        self.fileName = name

        if os.path.exists(name):
          self.load(name) 

# 
   def load(self,name = None):
      '''load file into array'''

      if name is not None:
         self.fileName = name

      try:
         self.fileHandle = open (self.fileName)
      except Exception as e:
	 # might be empty or does not exist, directory should exist, this will be tested
         self.fileLength = 0
         self.lastException = e
         return

      for line in self.fileHandle:
         line = line.strip()
         self.fileArray.append(line)

# adds a line

   def add(self, line):
      '''appends line to end of file'''
      self.fileArray.append(line)

# write

   def write(self):
      '''writes current buffer to file'''

      if self.fileHandle is not None:
         self.fileHandle.close()

      try:
         self.lastException = None
         self.fileHandle = open(self.fileName, 'w');
      except Exception as e:
         self.lastExcpetion = e	
         return

      for item in self.fileArray:
         self.fileHandle.write(item+'\n')
 
      self.fileHandle.close()

#
# will handle extensions and their configuration
#

class wikiExtension:
    'extension management class'

    def __init__(self, name, init_file = None):

      self.parameters = {}

      if init_file is None:
         self.init_fullpath = 'extensions/' + name + '/' + name + '.php' 

    def setParameter(self, name, value = None):
      '''change a parameter'''

      if value is None:
         value = ''

      self.parameters[name] = value 

    def writeParameters(self, config):
      '''write all parameters to specified settings object'''
     
      if isinstance(config,settings):
         for item in self.parameters.keys():
            if re.search('^\$',item) is None:
              line = ' $' + item + '="' + self.parameters[item] + '";' 
            else:
              line = ' ' + item + '="' + self.parameters[item] + '";' 

            config.add(line);
      else:
         raise Exception('invalid object type to writeParameters()');

    def write(self, config):
      '''initial wikiExtension support'''

      if isinstance(config,settings):
         config.add('$fn = "$IP/' + self.init_fullpath + '";');
         config.add('');
         config.add('if (file_exists($fn)) {');
         config.add(' require_once ($fn);');

         if len(self.parameters) > 0:
            self.writeParameters(config);

         config.add('}');
         config.add('');
         config.add('## EOF ##');
      else:
         raise Exception('invalid object type to write()');

#
class htaccess(settings):
   '''create .htaccess file'''

   destDir = None

   def __init__(self, wiki):
     if isinstance(wiki, mkwiki):
        destDir = wiki.destDir
        super(htaccess, self).__init__(destDir + '/.htaccess')

        self.add('RewriteEngine on');
        self.add('');


#
# handles custom configuratios
# LocalSettings.php will be left almost untouched apart from parameters we allow changing
# customsettings should be saved also in a binary file or in a database so to better
# handle automatic rebuild.. more details TBD
#
# This class might be removed as its features should be integrated with
# the mkwiki class
#

class customSettings(settings):
     'manage custom settings'

     def __str__(self):
        return self.fileName

     def __init__(self, wiki = None):
        self.id = None           # wiki id from mkwiki class 

        if isinstance(wiki, mkwiki):
           self.localsettings = wiki.LocalSettings.fileName
           self.id = wiki.id
           super(customSettings, self).__init__(wiki.destDir + "/" + "CustomSettings.php")

     def show(self):
        '''show contents of customarray'''

        for line in self.fileArray:
           print(line)

# "master" wiki generation class

class mkwiki:
   'wiki creation class - naming convention to be reviewed!!!'

   __version__ = '0.0.2'
   adminUser = 'admin'
   dbType = 'sqlite'
   phpSep = "/"

   def __init__(self, site_domain, site_id, full_url = None, wiki_name = None):

     self.LocalSettings = None
     self.destDir = None
     self.wikiName = None
     self.installCmd = None

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
     self.LocalSettings = settings(self.destDir + "/" + "LocalSettings.php")

# authentication

   def setupAuth(self, username = None, pw = None):
     '''setup default wiki username and password'''

     if username is None:
       if self.adminUser is None:
         self.adminUser = 'admin'
     else:
       self.adminUser = username

     if pw is None:
       self.adminPass = self.id + "0x"
     else:
       self.adminPass = pw

# internal configs - will be stored in a config file - sqlite or xml

   def setupInternals(self):
     '''setup for platform related variables'''
     #directory where php is installed: a way to dynamically configure this is needed

     _platform = platform.wikiPlatform()
        
     self.phpPath = _platform.phpPath
     self.rootDir = _platform.rootDir

     # where all html will be located
     self.destDir = self.rootDir + "/" + self.id + "/" + "html"
     # rootDir/id/db/ - this will be used by native installer
     self.dataDir = self.rootDir + "/" + self.id + "/" + "db"

     #install.php
     self.phpFile= self.destDir + "/maintenance/install.php"

     #php executable
     self.phpCmd = self.phpPath + "/" + "php"

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
     self.fulldbpath = self.dataDir + '/' + self.dbname + ".sqlite"

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
     print(cur.fetchone())

# prepares strings to be executed

   def prepareInstallCmd(self):
     ####
     #cygwin variables: phpFile & datPath
     # these must be changed to a windows format if using cygwin BUT Apache is Windows Native
     if self.is_cygwin:
       dataDir = subprocess.check_output(["cygpath", "-w", self.dataDir]);
       dataDir = dataDir.replace('\n','');
       phpFile = subprocess.check_output(["cygpath", "-w", self.phpFile]);
       phpFile = phpFile.replace('\n','');
       print('original phpFile  is ' + self.phpFile)
       print('cygwin phpFile  is ' + phpFile)

       self.installCmd = (self.phpCmd + ' "'   + phpFile         + '"' +
			  ' --dbpath="'        + dataDir         + '"' +
			  ' --dbtype="'        + self.dbType     + '"' +
			  ' --wiki="'          + self.id         + '"' +
			  ' --pass="'          + self.adminPass  + '"' +
			  ' --server="'        + self.wikiUrl    + '"' +
			  ' --dbname="'        + self.dbname     + '"' +
			  ' --scriptpath="'    + self.scriptpath + '"' +
			  ' --dbserver="'      + self.dbserver   + '"' +
			  ' "' + self.wikiName  + '" ' + self.adminUser
			)
       return
       
# load mkwiki configuration
   def run(self):
       #TBD: if installCmd is empty or not set should we return, try to "prepare" it or... ??
       if self.installCmd == "" or self.installCmd is None:
         return

       if os.path.exists(self.LocalSettings.fileName):
         print('already installed: ' + self.domain)
         return

       print("executing: " + self.installCmd)
       subprocess.call(self.installCmd,shell=True);

       self.postInstall()

       return

   def  postInstall(self):
     '''execute any post install step if needed'''
     # sqlite "database" must be writeable by webserver
     if self.dbType == 'sqlite':
       flags = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IWOTH | stat.S_IROTH
       os.chmod(self.fulldbpath, flags)
       os.chmod(self.dataDir, flags)

# print LocalSettings - to be removed
   def printSettings(self):
     '''print cotents of LocalSettings.php file - might be removed'''
     confArray = []
     filtComments   = re.compile(r'^#')
     filtEmptyLines = re.compile(r'^$')
     for line in self.LocalSettings.fileArray:
       line = line.strip()
       if filtComments.match(line) or filtEmptyLines.match(line):
         continue
       print(line)
       confArray.append(line)

     print('')
     print('Length: ' + str(len(confArray)))

# debug/info use only

   def printEnv(self):
     '''print internal variables - debug/test use'''
     print("id             = " + self.id)
     print("domain         = " + self.domain)
     print("phpPath        = " + self.phpPath)
     print("rootDir        = " + self.rootDir)
     print("dataDir        = " + self.dataDir)
     print("wikiUrl        = " + self.wikiUrl)
     print("wikiName       = " + self.wikiName)
     print("phpCmd         = " + self.phpCmd)
     print("LocalSettings  = " + self.LocalSettings.fileName)
     print("fulldbpath     = " + self.fulldbpath)
     print("destDir        = " + str(self.destDir))
     print("phpFile        = " + str(self.phpFile))
     print("installCmd     = " + str(self.installCmd))
     print("adminUser      = " + str(self.adminUser))
     print("adminPass      = " + str(self.adminPass))
     print("dbserver       = " + str(self.dbserver))
     print("is_cygwin      = " + str(self.is_cygwin))
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

## EOF ##
