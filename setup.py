#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#*********************************************************************************************************
#*   __     __               __     ______                __   __                      _______ _______   *
#*  |  |--.|  |.---.-..----.|  |--.|   __ \.---.-..-----.|  |_|  |--..-----..----.    |       |     __|  *
#*  |  _  ||  ||  _  ||  __||    < |    __/|  _  ||     ||   _|     ||  -__||   _|    |   -   |__     |  *
#*  |_____||__||___._||____||__|__||___|   |___._||__|__||____|__|__||_____||__|      |_______|_______|  *
#*http://www.blackpantheros.eu | http://www.blackpanther.hu - kbarcza[]blackpanther.hu * Charles K Barcza*
#*************************************************************************************(c)2002-2019********

import os, sys, time

def update_messages():
    pkgname="pycoder6"
    os.system("rm -rf .tmp")
    os.makedirs(".tmp")
    os.system("mkdir -p po")
    os.system("""find . -type f -name '*.py' -print |xargs \
     xgettext --default-domain=%s --keyword=_ --keyword=i18n --keyword=ki18n \
              --package-name='PyCoder6' \
              --package-version=0.5.4 \
              --copyright-holder='blackPanther Europe' \
              --msgid-bugs-address=info@blackpantheros.eu \
              -o po/tmp.pot *.py""" % (pkgname))
    print("Scan done!")
    time.sleep(3)
    os.system("msgcat --use-first po/tmp.pot >po/%s.pot" % (pkgname))
    os.system("rm po/tmp.pot")

    for item in os.listdir("po"):
        if item.endswith(".po"):
            os.system("msgmerge -q -o .tmp/temp.po po/%s po/%s.pot" % (item, pkgname))
            os.system("cp .tmp/temp.po po/%s" % item)

    os.system("rm -rf .tmp")


import cx_Freeze
import tempfile
def run_setup():
    tdir = tempfile.mkdtemp()
    scriptfile = os.path.join(tdir,"script.py")
    distdir = distdir = os.path.join(tdir,"dist")
    with open(scriptfile,"w") as f:
        f.write("import signedimp.crypto.rsa\n")
    f = cx_Freeze.Freezer([cx_Freeze.Executable(scriptfile)]) #,
                          #targetDir=distdir)
    f.freeze()
    if sys.platform == "win32":
        self.scriptexe = os.path.join(self.distdir,"script.exe")
    else:
        self.scriptexe = os.path.join(distdir,"script")


update_messages()
print("Translations is updated!")
#run_setup()
sys.exit(0)

