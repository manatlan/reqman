import reqman, asyncio,pytest
from pprint import pprint

MOCK={
    "/a":(200,"ok"),
}

def test_simple(exe):  
    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
- GET: /<<i|method>>
  headers:
    x-hello: world
  params:
    i: 0
    method: return 12/x
  tests:
    - status: 200
- GET: /<<i|method>>
  headers:
    x-hello: world
  params:
    i: 0
  tests:
    - status: 200
- GET: /a
  headers:
    x-hello: <<i|method>>
  params:
    i: 0
  tests:
    - status: 200
- POST: /a
  body: <<i|method>>
  headers:
    x-hello: world
  params:
    i: 0
    method: return 12/x
  tests:
    - status: 200

""")
        
    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 4

def test_py_in_save(exe):  
    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
- GET: /a
  save: 
    r: <<i|method>>
  params:
    i: 0
    method: return 12/x
  tests:
    - status: 200
""")
        
    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 1

def test_py_in_foreach(exe):  
    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
- GET: /a
  foreach: <<i|method>>
  params:
    i: 0
    method: return 12/x
  tests:
    - status: 200
""")
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == -1 # real error
