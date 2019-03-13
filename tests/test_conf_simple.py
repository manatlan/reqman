#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim/
"""),
    dict(name="test.yml",content="""
- GET: /yo
  tests:
    - status: 200

- GET: yo
  tests:
    - status: 200
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all tests ok
    # assert x.console.count("GET /yo --> 200") == 2

def test_2(client):
    x=client( "test.yml","--ko")
    assert x.code==0 # all tests ok
    # assert x.console.count("GET /yo --> 200") == 0

