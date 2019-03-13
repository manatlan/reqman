#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://x/t" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="test1.yml",content="""
- GET: http://x/t
"""),
    dict(name="test2.yml",content="""
- GET: http://x/t
  tests:
    - status: 200
    - content: dsq
"""),
]

def test_1(client):
    x=client( "test1.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==0
    assert x.inproc.ok==0
    assert len(x.inproc.reqs)==1
    # assert "GET /t --> 200" in x.console


def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
    # assert "GET /t --> 200" in x.console

def test_3(client):
    x=client( "*" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==2
    # assert "GET /t --> 200" in x.console

