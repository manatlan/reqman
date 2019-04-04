#!/usr/bin/python
# -*- coding: utf-8 -*-



SERVER={
    "GET http://jim/yo" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="reqman.conf",content="""
root: http://jim/
- fdsq: fds
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert "ERROR: bad param" in x.console

def test_2(client):
    x=client( "." )
    assert "ERROR: YML syntax in" in x.console
