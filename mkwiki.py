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
# 0.0.3
#       code made into a module
#

import sys

# our new module
from mkwiki import *

#


def main(argv=None):
   if argv is None:
      argv = sys.argv
 
   if len(argv) == 1:
      fqdn="c.20wiki.net"
      id="c_20wiki_net"
   else:
      if len(argv) == 2:
        fqdn = argv[1]
        id = fqdn.replace('.','_')
      else:
        fqdn = argv[1]
        id = argv[2]
 
   urlPath = 'w'
   print 'Full Domain: ' + fqdn
   print 'Wiki ID: ' + id
   print 
 
   try:
     wi = mkwiki.mkwiki(fqdn, id, None, 'Test Wiki') # fqdn, wiki id, full url, wiki name
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

   # CustomSettings.php
   cs = mkwiki.customSettings(wi)

   cs.add('<?php');
   cs.add('#this is a test comment');
   cs.add('');

   if urlPath is None:
     cs.add('$wgArticlePath      = "/$1";');
   else:
     if len(urlPath) > 0:
       cs.add('$wgArticlePath      = "/' + urlPath + '/$1";');
     else:
       cs.add('$wgArticlePath      = "/$1";');

   # $wgLogo set incorrectly by 1.21.x installer
   cs.add('');
   cs.add('$wgLogo             = "$wgStylePath/common/images/wiki.png";');

   # basic wikiExtension test
   ext = mkwiki.wikiExtension('SyntaxHighlight_GeSHi');
   ext.write(cs);

   # save customsettings to disk
   cs.write()
  
   # .htaccess
   hta = mkwiki.htaccess(wi)


   hta.add('RewriteEngine On')
   hta.add('')
   hta.add('RewriteCond %{REQUEST_FILENAME} !-f')
   hta.add('RewriteCond %{REQUEST_FILENAME} !-d')
   if urlPath is None:
     hta.add('RewriteRule ^/?(.*)$ /index.php?title=$1 [L,QSA]')
   else:
     if len(urlPath) > 0:
       hta.add('RewriteRule ^' + urlPath + '/?(.*)$ /index.php?title=$1 [L,QSA]')
     else:
       hta.add('RewriteRule ^/?(.*)$ /index.php?title=$1 [L,QSA]')
   hta.write()

   # LocalSettings.php
   ls = wi.LocalSettings

   ls.load() # load created file
   ls.add('$cs="CustomSettings.php";')
   ls.add('');
   ls.add('if (file_exists($cs)) {');
   ls.add('  include_once($cs);');
   ls.add('}');

   ls.write()

if __name__ == "__main__":
   sys.exit(main())
  
## EOF ##
