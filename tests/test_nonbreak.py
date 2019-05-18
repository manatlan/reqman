#!/usr/bin/python
# -*- coding: utf-8 -*-

import json,os,shutil

SERVER={
    "/query" : (200, json.dumps({"next":"continue"})),
    "/nimp" : (500, "E/R\\R:{']OR"),
    "/continue" : (200, json.dumps({"next":"ok"})),
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


    dict(name="test_path_ko.yml",content="""
- POST: http://x/nimp
  tests:
    - status: 200
  save: r
- GET: http://x/mycontent/xxx-<<r.result.0.val>>-<<r.result.1.val>>-{{yolo}}
  tests:
    - status: 200
    - content: ok
"""),
]

def test_scenar(client):
    x=client( "test_scenar.yml" )
    assert x.code==0 # 0 error
    assert len(x.inproc.reqs[0])==3
    assert x.inproc.ok == x.inproc.total == 6
    assert x.html


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
    assert x.html            # a reqman.html is generated (the most important)

    assert x.code==1                                # 1 errors (1 req non playable with 1 test in error)
    assert x.inproc.ok == 5
    assert x.inproc.total == 6
    assert len(x.inproc.reqs[0])==3                 

def test_path_break(client):
    x=client("test_path_ko.yml")
    assert x.code==3
    assert x.inproc.ok == 0
    assert x.inproc.total == 3

