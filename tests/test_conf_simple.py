#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/yo" : ( 200,"dsq")
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
    - status: 300
"""),
    dict(name="test2.yml",content="")
]

def test_1(client):
    x=client( "." )
    assert x.code==1 # 1 error

def test_2(client):
    x=client( ".","--ko")
    assert x.code==1 # 1 error

