#!/usr/bin/python3
# -*- coding: utf-8 -*-
import reqman
assert reqman.main

import os,sys,shutil
from PyInstaller import __main__ as py

##################################################################
if not "win" in sys.platform.lower():
    print("Only on windows ;-)")
    sys.exit(-1)
##################################################################

def rm(f):
    if os.path.isdir(f):
        shutil.rmtree(f)
    elif os.path.isfile(f):
        os.unlink(f)

try:
    os.chdir(os.path.split(sys.argv[0])[0])

    py.run([
        'reqman/__main__.py',
        "-n","reqman",
        '--onefile',
        '--noupx',
        "--exclude-module","tkinter",
        '--icon="dist/reqman.ico"'
    ])

    os.system("""dist\\verpatch.exe dist\\reqman.exe %s /high /va /pv %s /s description "Commandline tool to test a http service with yaml's scenarios (more info : https://github.com/manatlan/reqman)" /s product "ReqMan" /s copyright "GPLv2, 2021" /s company "manatlan" """ % reqman.__version__)
finally:
    rm("reqman.spec")
