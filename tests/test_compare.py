#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client
import json


SERVER={
    "/t" : (200, json.dumps(dict(value=42,liste=[1,2,3],txt="hello",d={"a":"b"},b=True))),
    "/tt" : (200, "i m not json"),
}

FILES=[
    dict(name="test1.yml",content="""
- GET: http://x/t
  tests:
    - Content-Type: text/plain
    - Content-Type: text
    - status: <<ok>>
    - status: 200
    - status: .=200
    - status: .>=100
    - status: .>100
    - status: .<300
    - status: .<=300
    - status: .!=500
    - status: .==200
    - json.value: 42
    - json.value: "42"
    - json.liste.size: 3
    - json.liste.0: 1
    - json.liste.1: 2
    - json.liste.2: 3
    - json.txt.size: 5
    - json.d.a: b
    - json.d.size: 1
    - json.b: true
    - content: hello
    - json.value:           # match any
        - 42
        - 43
    - content:
        - hello
        - bonjour
  params:
    ok: 200
"""),
    dict(name="test2.yml",content="""
- GET: http://x/tt
  tests:
    - json.result: ok
"""),
]

def test_1(client):
    x=client( "test1.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==x.inproc.ok

def test_2(client):
    x=client( "test2.yml" )
    assert x.code==1 # 1 error
    assert x.inproc.total==1
    assert x.inproc.ok==0
