#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="test.yml",content="""
- GET: /yo
  tests:
    - status: 200
    - content: dsq
  foreach: <<a_liste>>
  params:
    a_liste:
        - v: 1
        - v: 2
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert len(x.inproc.reqs[0])==2
