#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim
"""),
    dict(name="test.yml",content="""
- GET: /yo
  tests:
    - status: 200
    - content: dsq
"""),
    dict(name="folder/test.rml",content="""
- GET: /yo
  tests:
    - status: 200
    - content: dsq
"""),

#     # hidden
#     dict(name="_hidden.yml",content="""
# - GET: /yo
#   tests:
#     - status: 200
#     - content: dsq
# """),

    # hidden
    dict(name="_folder/test.rml",content="""
- GET: /yo
  tests:
    - status: 200
    - content: dsq
"""),

]

def test_conf_local(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    assert "GET /yo --> 200" in x.console


def test_get_conf_from_parent(client):
    x=client( "folder/test.rml" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    assert "GET /yo --> 200" in x.console

def test_get_all_tests1(client):
    x=client( "." )
    assert x.code==0 # all ok
    assert x.inproc.total==4
    assert x.inproc.ok==4
    assert len(x.inproc.reqs)==2
    assert "GET /yo --> 200" in x.console

def test_get_all_tests2(client):
    x=client( "test.yml","folder" )
    assert x.code==0 # all ok
    assert x.inproc.total==4
    assert x.inproc.ok==4
    assert len(x.inproc.reqs)==2
    assert "GET /yo --> 200" in x.console


def test_folder(client):
    x=client( "folder" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    assert "GET /yo --> 200" in x.console

def test_pattern1(client):
    x=client( "t*" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    assert "GET /yo --> 200" in x.console

def test_pattern2(client):
    x=client( "f*" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    assert "GET /yo --> 200" in x.console
