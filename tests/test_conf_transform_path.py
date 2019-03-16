#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client
import os

SERVER={
    "/yo" : lambda q: (200, q.body),
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim/

method: return os.path.isfile("reqman.conf") and "ok" or "ko"
"""),
    dict(name="folder/test.yml",content="""
- POST: /yo
  body:
    <<|method>>
  tests:
    - status: 200
    - content: ok

"""),
]

def test_path_during_method_is_where_rc_is(client):
    x=client( "." )
    assert x.code==0
