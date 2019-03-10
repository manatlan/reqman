#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="jim"),
    "GET http://jom/yo" : lambda q: dict( status=200, body="jom"),
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim/

switch1: 
    root: http://jom/
"""),
    dict(name="test.yml",content="""
- GET: /yo
  tests:
    - status: 200

"""),
]

def test_1(client):
    x=client( )
    assert x.code==-1
    assert "-switch1 :" in x.console

    x=client( "." )
    assert x.code==0
    assert x.inproc.ok == x.inproc.total

    x=client( ".","-switch1" )
    assert x.code==0
    assert x.inproc.ok == x.inproc.total

