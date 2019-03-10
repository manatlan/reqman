#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    # "GET http://x/t" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="test1.yml",content="""
- call: yo
"""),
    dict(name="test2.yml",content="""
- GET: <<yo>>
"""),
    dict(name="test3.yml",content="""
- GET: <<42|yi>>
"""),
    dict(name="test4.yml",content="""
- GET: <<42|yi>>
  params:
    yi: fdsqfsdqfdsfdsfdsq
"""),
    dict(name="test5.yml",content="""
- GET: <<42|yi>>
  params:
    yi: fdsqfsdqfd sfdsfdsq
"""),
    dict(name="test6.yml",content="""
- GET: http://x/x
  POST: http://x/x
"""),

]

def test_1(client):
    x=client( "test1.yml" )
    assert x.code==-1
    assert "ERROR: unknown procedure 'yo'" in x.console

def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0
    assert "GET <<yo>> --> Not callable" in x.console

def test_3(client):
    x=client( "test3.yml" )
    assert x.code==0
    assert "GET <<42|yi>> --> Not callable" in x.console

def test_4(client):
    x=client( "test4.yml" )
    assert x.code==-1
    assert "ERROR: Error in execution of method yi" in x.console

def test_5(client):
    x=client( "test5.yml" )
    assert x.code==-1
    assert "ERROR: Error in declaration of method yi" in x.console

def test_6(client):
    x=client( "test6.yml" )
    assert x.code==-1
    assert "ERROR: no action or too many" in x.console
