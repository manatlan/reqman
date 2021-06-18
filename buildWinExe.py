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

def conv(v): # conv versionning to windows x.x.x.x
    a,b,c=v.split(".")
    clean=lambda x: x and x.isnumeric() and x or "0"
    return ".".join([clean(a), clean(b), clean(c), "0"])

assert conv("1.2.3") == "1.2.3.0"
assert conv("1.2.3a") == "1.2.0.0"

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
        '--icon=dist/reqman.ico'
    ])

    v=conv(reqman.__version__)
    os.system(f"""dist\\verpatch.exe dist\\reqman.exe {v} /high /va /pv {v} /s description "Commandline tool to test a http service with yaml's scenarios (more info : https://github.com/manatlan/reqman)" /s product "Reqman" /s copyright "GPLv2, 2021" /s company "manatlan" """)
finally:
    rm("reqman.spec")
