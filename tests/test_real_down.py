#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client

FILES=[
    dict(name="test.yml",content="""
- GET: http://fdsqfdsq/t

"""),
]

def test_real_server_down(client):
    x=client( "*" )
    assert x.code==0
    assert "ERROR: Server is down" in x.console
    assert "ERROR: Server is down" in x.html
    assert x.inproc.total==0
    assert x.inproc.ok==0
    assert len(x.inproc.reqs)==1