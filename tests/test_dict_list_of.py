#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://x/t" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="normal.yml",content="""
- GET: http://x/t
  headers:
    jo: hello
  tests:
    - content: dsq
"""),
    dict(name="invert.yml",content="""
- GET: http://x/t
  headers:
    - jo: hello
  tests:
    content: dsq
"""),
]

def test_1(client):
    x=client( "normal.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==x.inproc.ok
    assert "***WARNING*** 'headers:' should be filled" not in x.console
    assert "***WARNING*** 'tests:' should be a list" not in x.console

def test_invert(client):
    x=client( "invert.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==x.inproc.ok
    assert "***WARNING*** 'headers:' should be filled" in x.console
    assert "***WARNING*** 'tests:' should be a list" in x.console
