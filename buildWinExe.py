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
    exe_name=f"reqman-{reqman.__version__}.exe"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # build PyInstaller arguments and detect UPX
    args = [
        'src/reqman/__main__.py',
        "-n", exe_name[:-4],
        '--onefile',
        "--exclude-module", "tkinter",
        '--icon=ressources/reqman.ico'
    ]

    upx_path = shutil.which('upx') or shutil.which('upx.exe')
    if upx_path:
        upx_dir = os.path.dirname(os.path.abspath(upx_path))

    if upx_dir:
        print(f"Using UPX from {upx_dir}")
        args.append(f"--upx-dir={upx_dir}")
    else:
        print("UPX not found or disabled; building without UPX")
        args.append('--noupx')

    py.run(args)

    v=conv(reqman.__version__)
    os.system(f"""ressources\\verpatch.exe dist\\{exe_name} {v} /high /va /pv {v} /s description "Commandline tool to test a http service with yaml's scenarios (more info : https://github.com/manatlan/reqman)" /s product "Reqman" /s copyright "GPLv2, 2021" /s company "manatlan" """)
finally:
    rm(exe_name[:-4]+".spec")
