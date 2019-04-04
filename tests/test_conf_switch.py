#!/usr/bin/python
# -*- coding: utf-8 -*-


SERVER={
    "http://jim/yo" : (200,"dsq"),
    "http://jom/yo" : (200,"dsq"),
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

