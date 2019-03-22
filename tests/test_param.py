#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/42" : (200, "ok"),
    "/41" : (200, "ok"),
    "/pingpong" : lambda q: (200, q.body),
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

    dict(name="test_param.yml",content="""
- POST: http://jim/pingpong
  body:
    a_true: <<a_true>>
    a_false: <<a_false>>
    a_none: <<a_none>>
    a_dict: <<a_dict>>
    a_list: <<a_list>>
    a_float: <<a_float>>
  params:
    a_true: True
    a_false: False
    a_none: null
    a_list:
        - 1
        - 2
        - 3
    a_dict:
        v: 42
    a_float: 1.42
  tests:
    - status: 200
    - json.a_true: True    
    - json.a_false: False
    - json.a_none: ""               # NOT TOP (should be null)
    - json.a_list: [1,2,3]
    - json.a_dict:
            v: 42
    - json.a_float: 1.42
"""),

    dict(name="test_not_really_an_error_param.yml",content="""
- POST: http://jim/pingpong
  body:
    not_an_error: <<unknow>>
  tests:
    - status: 200
"""),
    dict(name="test_error_param.yml",content="""
- POST: http://jim/pingpong
  body:
    an_error: <<v>>
  params:
    v: <<unknown>>  # in this case : it's an error
  tests:
    - status: 200
"""),

    dict(name="test_param_resolve_inside.yml",content="""
- POST: http://jim/pingpong
  body: <<data>>
  params:
    data:
      myval: <<v>>
      myval2: <<another>>
      myres: <<3|stampfel>>
    v: 42
    another: <<another2>>
    another2: <<v>>
    stampfel: return x*"yo"
  tests:
    - status: 200
    - json.myval: 42
    - json.myval2: 42
    - json.myres: yoyoyo
    
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

def test_param_typed(client):
    x=client( "test_param.yml" )
    assert x.code==0

def test_not_really_an_error_param(client):
    x=client( "test_not_really_an_error_param.yml" )
    assert x.code==0 # it works, param is not resolved, considered as is


def test_error_param(client):
    x=client( "test_error_param.yml" )
    assert x.code==-1
    assert "ERROR: Can't resolve unknown" in x.console

def test_param_resolve(client):
    x=client( "test_param_resolve_inside.yml" )
    with open("/home/manatlan/aeff.html","w+") as fid:
        fid.write(x.html)
    assert x.code==0
    # assert "ERROR: Can't resolve unknown" in x.console
