#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/42" : lambda q: dict( status=200, body="ok"),
    "GET http://jim/41" : lambda q: dict( status=200, body="ok"),
}

FILES=[
    dict(name="test.yml",content="""
- GET: http://jim/{{yo}}
  params:
    yo: 42
  tests:
    - status: 200
    - content: ok    
"""),
    dict(name="test2.yml",content="""
- proc:
    - GET: http://jim/{{yo}}
- call: proc
  params:
    yo: 42
  tests:
    - status: 200
    - content: ok    
"""),

    dict(name="test3.yml",content="""
- proc:
    - GET: http://jim/{{yo}}
      params:
        yo: 41
- call: proc
  params:
    yo: 42
  tests:
    - status: 200
    - content: ok    
"""),

    dict(name="test4.yml",content="""
- proc:
    - GET: http://jim/{{yo}}
      params:
        yo: 41
- call: proc
  tests:
    - status: 200
    - content: ok    
"""),

    dict(name="test10.yml",content="""
- proc:
    - GET: http://jim/{{41|add1}}
- call: proc
  params:
    add1: return x+1
  tests:
    - status: 200
    - content: ok    
"""),
]

def test_simple(client):
    x=client( "test.yml" )
    assert x.code==0
    assert x.inproc.total==2
    assert x.inproc.ok==2    

def test_simple_proc(client):
    x=client( "test2.yml" )
    assert x.code==0
    assert x.inproc.total==2
    assert x.inproc.ok==2    

def test_simple_proc_override_param(client):
    x=client( "test3.yml" )
    assert x.code==0
    assert x.inproc.total==2
    assert x.inproc.ok==2    

def test_simple_proc_param(client):
    x=client( "test4.yml" )
    assert x.code==0
    assert x.inproc.total==2
    assert x.inproc.ok==2    

def test_param_method(client):
    x=client( "test10.yml" )
    assert x.code==0
    assert x.inproc.total==2
    assert x.inproc.ok==2    
