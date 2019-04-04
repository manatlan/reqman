#!/usr/bin/python
# -*- coding: utf-8 -*-
# 


SERVER={
    "/t" : (200,"dsq")
}

FILES=[
    dict(name="test1.yml",content="""
- GET: http://x/t
  tests:
    - status: 200
    - content: dsq
- break
- GET: http://x/t
  tests:
    - status: 200
    - content: dsq
"""),
]

def test_break(client):
    x=client( "test1.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2
    assert len(x.inproc.reqs)==1
