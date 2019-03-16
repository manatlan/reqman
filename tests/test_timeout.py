#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/yo" : ( 200,"dsq")
}

FILES=[
    dict(name="test.yml",content="""
- yolo:
    - GET: http://jim/yo
      tests:
        - status: 200
        - content: dsq
- call: yolo
  params:
    timeout: fdsqfdsqfds # bad timeout (int !)
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert len(x.inproc.reqs[0])==1
    assert repr(x.inproc.reqs[0][0]).startswith("<GET")
