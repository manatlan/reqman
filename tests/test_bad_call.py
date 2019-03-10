#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client

FILES=[
    dict(name="yo.txt",content="jkjkjk"),
]

def test_no_param(client):
    x=client( )
    assert x.code == -1
    assert "https://github.com/manatlan/reqman" in x.console # display usage
    assert x.html is None
    
def test_bad_yml(client):
    x=client( "yo.txt")
    assert x.code == -1
    assert "ERROR: no actions" in x.console # display usage
    assert x.html is None

def test_asterisk(client):
    x=client( "*")
    assert x.code == -1
    assert "ERROR: no actions" in x.console # display usage
    assert x.html is None

def test_bad_switch(client):
    x=client( "-dua","*")
    assert x.code == -1
    assert "ERROR: the switch" in x.console # display usage
    assert x.html is None

def test_bad_call(client):
    x=client( "nimp.yml")
    assert x.code == -1
    assert "ERROR: bad param" in x.console # display usage
    assert x.html is None
