#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim

BEGIN:
    - GET: /yo
      tests:
        - status: 200
        - content: dsq

END:
    GET: /yo
    tests:
        - status: 200
        - content: dsq

"""),
    dict(name="test.yml",content="""
- GET: /yo
  tests:
    - status: 200
    - content: dsq
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert x.inproc.total==6
    assert x.inproc.ok==6
    assert len(x.inproc.reqs)==3        # 3 groups
    assert len(x.inproc.reqs[0])==1
    assert len(x.inproc.reqs[1])==1
    assert len(x.inproc.reqs[2])==1

