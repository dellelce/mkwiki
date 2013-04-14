#!/usr/bin/env python
#
# mediawiki installation tool
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

import os
import re
import subprocess
import array
import sqlite3

class mkwiki:
   'wiki creation class'

   def __init__(self, site_domain, site_id):

       self.version = "0.0.1"

       if self.test_cygwin:
         self.is_cygwin = True
       else:
	 self.is_cygwin = False

       print "welcome to mkwiki " + self.version

       self.id = site_id
       self.domain = site_domain

       #internal objects - dependant on system configuration/apache install/etc
       self.setupInternals()

       #install.php
       self.phpFile= self.destDir + "/maintenance/install.php"
       #used only internally - full command with arguments
       self.installCmd=""
       # password
       self.adminpass = self.id + "0x"
       # wikiUrl
       self.wikiUrl = "http://" + self.id + ".net"
       # dbname (will be filename for sqlite?)
       self.dbname = self.id + "_db"
       # full db pat - this is used internally, so no need to use cygpath if under cygwin
       self.fulldbpath = self.dataDir + "/" + self.dbname + ".sqlite"
       #
       # scriptpath .. currently empty
       self.scriptpath = ""
       # configuration files
       self.LocalSettings = self.destDir + "/" + "LocalSettings.php"
       ####
       #cygwin variables: phpFile & datPath
       # these must be changed to a windows format if using cygwin BUT Apache is Windows Native
       if self.is_cygwin:
	 self.dataDir = subprocess.check_output(["cygpath", "-w", self.dataDir]);
	 self.dataDir = re.sub(r'\', '', self.dataDir);
	 self.phpFile = subprocess.check_output(["cygpath", "-w", self.phpFile]);
	 self.phpFile = re.sub(r'\', '', self.phpFile);

# internal configs

   def setupInternals(self):
       #directory where phop is installed: a way to dynamically configure this is needed
       self.phpDir = "/c/apache/php5"
       # directory where all websites are
       self.rootDir = "/c/apache/sites"
       # where all html will be located
       self.destDir = self.rootDir + "/" + self.id + "/" + "html"
       # rootDir/id/db/
       self.dataDir = self.rootDir + "/" + self.id + "/" + "db"

       #php executable
       self.phpCmd = self.phpDir + "/" + "php"
       # dbserver.. not really needed for sqlite
       self.dbserver = "localhost"

# slightly different behaviour if we are using cygwin

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
       self.installCmd = (self.phpCmd + ' "' + self.phpFile + '"' +
			  ' --dbpath="'        + self.dataDir + '" ' +
			  ' --dbtype="sqlite"' +
			  ' --wiki="'          + self.id + '" ' +
			  ' --pass="'          + self.adminpass + '" ' +
			  ' --server="'        + self.wikiUrl + '" ' +
			  ' --dbname="'        + self.dbname + '" ' +
			  ' --scriptpath="'    + self.scriptpath + '" ' +
			  ' --dbserver="'      + self.dbserver + '" ' +
			   self.id + ' ' + self.id
			)
       return
       
# load mkwiki configuration
   def run(self):
       if self.installCmd != "":
	print "executing: " + self.installCmd
	subprocess.call(self.installCmd,shell=True);
	subprocess.call(["chmod", "777", self.fulldbpath]);
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
       fh.close
  
# debug/info use only
 
   def printEnv(self):
       print "id             = " + self.id
       print "domain         = " + self.domain
       print "phpDir         = " + self.phpDir
       print "rootDir        = " + self.rootDir
       print "dataDir        = " + self.dataDir
       print "wikiUrl        = " + self.wikiUrl
       print "phpCmd         = " + self.phpCmd
       print "LocalSettings  = " + self.LocalSettings
       print "fulldbpath     = " + self.fulldbpath
       print "destDir        = " + str(self.destDir)
       print "phpFile        = " + str(self.phpFile)
       print "installCmd     = " + str(self.installCmd)
       print "adminpass      = " + str(self.adminpass)
       print "dbserver       = " + str(self.dbserver)
       print "is_cygwin      = " + str(self.is_cygwin)
       return
   
   def htaccessRaw(self):
       print "this is htaccessRaw"
       return

   def readConfig(self, config="mkwiki.config"):
       dbConn = sqlite3.connect(self.fulldbpath) #warning should perform some tests..
       cur = dbConn.cursor()
       #cur.execute ("select page_id,page_namespace,page_is_new, page_title from page");
       return


wi = mkwiki('20wiki.net', '20wiki') # domain, id
   
wi.prepareInstallCmd()
wi.printEnv()
wi.run()
wi.printSettings()
#wi.testDB()


## EOF ##
