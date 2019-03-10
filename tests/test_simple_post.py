#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "POST http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="test.yml",content="""
- POST: http://jim/yo
  body: <<value|encode>>
  params:
    value: ['1','2','3']
    encode: return "|".join(x)
  tests:
    - status: 200
"""),
    dict(name="test2.yml",content="""
- POST: http://jim/yo
  body: 
    koko:
        - 12
        - 23
    type:
        value: 42
        label: fortytwo

  tests:
    - status: 200
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all tests ok

def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0 # all tests ok
