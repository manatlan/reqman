#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client
import json,os,shutil

SERVER={
    "/query" : (200, json.dumps({"next":"continue"})),
    "http://<<unknown>>/query" : (200, json.dumps({"next":"continue"})),
    "/doit" : lambda q: (200, q.body),
}

FILES=[

    dict(name="test_scenar.yml",content="""
- GET: http://x/query
  tests:
    - status: 200
    - json.next: continue
  save: r
- POST: http://x/doit
  body: <<myparam>>
  params:
    myparam: <<r.next>>
  tests:
    - status: 200
    - content: continue
- GET: http://x/query
  tests:
    - status: 200
    - json.next: continue
"""),

    dict(name="test_scenar_ko.yml",content="""
- GET: http://x/query
  tests:
    - status: 200
    - json.next: continue
##########################################################  save: r
- POST: http://x/doit
  body: <<myparam>>
  params:
    myparam: <<r.next>>
  tests:
    - status: 200
    - content: continue
- GET: http://x/query
  tests:
    - status: 200
    - json.next: continue
"""),

    ## non problematic tests
    dict(name="test_10.yml",content="""
- GET: http://x/query
  body: <<unknown>>
  tests:
    - status: 200
"""),
    dict(name="test_11.yml",content="""
- GET: http://x/query
  headers:
    content-type: <<unknown>>
  tests:
    - status: 200
"""),

    dict(name="test_12.yml",content="""
- GET: http://x/query
  tests:
    - status: <<unknown>>
"""),

    dict(name="test_13.yml",content="""
- GET: http://<<unknown>>/query
  tests:
    - status: 200
"""),


]

def test_scenar(client):
    x=client( "test_scenar.yml" )
    assert x.code==0 # 0 error
    assert len(x.inproc.reqs[0])==3
    assert x.inproc.ok == x.inproc.total == 6
    assert os.path.isfile("reqman.html")


def test_non_problematic(client):
    x=client( "test_10.yml" )
    assert x.code==0                                # no problem unknow is not resolved, considered as is
    assert x.inproc.ok == x.inproc.total == 1

    x=client( "test_11.yml" )
    assert x.code==0                                # no problem unknow is not resolved, considered as is
    assert x.inproc.ok == x.inproc.total == 1

    x=client( "test_12.yml" )
    assert x.code==1                               # # no problem unknow is not resolved, considered as is ... but test fail
    assert x.inproc.ok == 0
    assert x.inproc.total == 1

    x=client( "test_13.yml" )
    assert x.code==0
    assert x.inproc.ok == 1
    assert x.inproc.total == 1

def test_scenar_break(client):
    x=client( "test_scenar_ko.yml" )
    assert os.path.isfile("reqman.html")            # a reqman.html is generated (the most important)
    shutil.copy2("reqman.html",r"c:\reqman.html")   # make a copy for me

    assert x.code==2                                # 2 errors (1 req non playable with 2 tests in error)
    assert x.inproc.ok == 4
    assert x.inproc.total == 6
    assert len(x.inproc.reqs[0])==3                 
