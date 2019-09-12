import pytest,reqman,json

MOCK={
    "https://www.manatlan.com/utf8":(200,"oké"),
    "https://www.manatlan.com/cp1252":(200,"oké".encode().decode("cp1252")),
}

def test_same_encoding(exe):  
    y="""
GET: https://www.manatlan.com/utf8
tests:
    - content: oké
"""

    with open("f.yml","w+") as fid:
        fid.write(y)
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0

def test_same_encoding2(exe): 
    y="""
GET: https://www.manatlan.com/cp1252
tests:
    - content: oké
""".encode().decode("cp1252")

    with open("f.yml","w+") as fid:
        fid.write(y)
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0

def test_diff_encoding(exe): 
    y="""
GET: https://www.manatlan.com/cp1252
tests:
    - content: oké
"""

    with open("f.yml","w+") as fid:
        fid.write(y)
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    # x.view()

def test_diff_encoding_with_rconf(exe): 
    y="""
GET: https://www.manatlan.com/cp1252
tests:
    - content: <<val>>
"""

    with open("f.yml","w+") as fid:
        fid.write(y)

    with open("reqman.conf","w+") as fid:
        fid.write("""val: oké""")
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    # x.view()

def test_diff_encoding_with_rconf2(exe): 
    y="""
- GET: https://www.manatlan.com/utf8
  tests:
    - content: <<val>>

- GET: https://www.manatlan.com/cp1252
  tests:
    - content: <<val>>
""".encode().decode("cp1252")

    with open("f.yml","w+") as fid:
        fid.write(y)

    with open("reqman.conf","w+") as fid:
        fid.write("""val: oké""".encode().decode("cp1252"))
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    # x.view()
