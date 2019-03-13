#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim

myproc:
    - GET: /yo
      tests:
        - status: 200
        - content: dsq

"""),
    dict(name="test.yml",content="""
- call: myproc
"""),
    dict(name="test2.yml",content="""
- call: myproc
  foreach:
    - v: 1
    - v: 2
    - v: 3
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs[0])==1
    # assert "GET /yo --> 200" in x.console


def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0 # all ok
    assert x.inproc.total==6
    assert x.inproc.ok==6
    assert len(x.inproc.reqs[0])==3
    # assert "GET /yo --> 200" in x.console

