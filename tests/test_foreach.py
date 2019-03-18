#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/yo" : ( 200, "dsq"),
}

FILES=[
    dict(name="test.yml",content="""
- GET: http://xxx/yo
  tests:
    - status: 200
    - content: dsq
  foreach: <<a_liste>>
  params:
    a_liste:
        - v: 1
        - v: 2
"""),
    dict(name="test2.yml",content="""
-   GET: http://xxx/yo
    tests:
        - status: 200
        - content: dsq
    foreach: <<2|mkliste>>
    params:
        mkliste: return x * [ {"v":1} ]
"""),
    dict(name="test3.yml",content="""
-   GET: http://xxx/yo
    tests:
        - status: 200
        - content: dsq
    foreach: <<bad_type>>
    params:
        bad_type:
            v: 1
            v: 2
"""),
    dict(name="test4.yml",content="""
- GET: http://xxx/yo
  tests:
    - status: 200
    - content: dsq
  foreach: <<a_liste>>
  params:
    a_liste:
        - v: 1
        - <<vvv>>
    vvv:
        v: 2
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2
def test_4(client):
    x=client( "test4.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2
def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2

def test_3(client):
    x=client( "test3.yml" )
    assert x.code==-1
