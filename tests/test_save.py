#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client
import os,json

SERVER={
    "GET http://jim/get_brut" : lambda q: dict( status=500, body="42"),
    "GET http://jim/get_json" : lambda q: dict( status=501, body=json.dumps(dict(value=42))),
    "GET http://jim/42" : lambda q: dict( status=200, body="ok"),
    "GET http://jim/not_json" : lambda q: dict( status=200, body="fdsq fdsq : fdsq !"),
}

FILES=[
    dict(name="test.yml",content="""
- GET: http://jim/get_brut
  tests:
    - status: 400
  save: val
- GET: http://jim/{{val}}
  tests:
    - status: 200
    - content: ok
"""),
    dict(name="test2.yml",content="""
- GET: http://jim/get_json
  tests:
    - status: 400
  save: val
- GET: http://jim/{{val.value}}
  tests:
    - status: 200
    - content: ok
"""),
    dict(name="test3.yml",content="""
- GET: http://jim/get_brut
  tests:
    - status: 500
  save: file://./aeff.html
"""),
    dict(name="test4.yml",content="""
- GET: http://jim/get_brut
  tests:
    - status: 500
  save: file://
"""),
   dict(name="test10.yml",content="""
- GET: http://jim/not_json
  tests:
    - status: 200
  save: val
"""),
]

def test_save_text(client):
    x=client( "test.yml" )
    assert x.code==1
    assert x.inproc.total==3
    assert x.inproc.ok==2

def test_save_json(client):
    x=client( "test2.yml" )
    assert x.code==1
    assert x.inproc.total==3
    assert x.inproc.ok==2

def test_save_file(client):
    x=client( "test3.yml" )
    assert x.code==0
    assert x.inproc.total==x.inproc.ok
    assert os.path.isfile("aeff.html")

def test_save_bad_file(client):
    x=client( "test4.yml" )
    assert x.code==-1
    assert "ERROR: Save to file" in x.console
    # assert x.inproc.total==x.inproc.ok
    # assert os.path.isfile("aeff.html")


def test_save_not_json(client):
    x=client( "test10.yml" )
    assert x.code==0
