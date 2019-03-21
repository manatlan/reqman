#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    # "GET http://x/t" : lambda q: dict( status=200, body="dsq")
}

FILES=[
    dict(name="test1.yml",content="""
- call: yo
"""),
    dict(name="test2.yml",content="""
- GET: <<yo>>
"""),
    dict(name="test3.yml",content="""
- GET: <<42|yi>>
"""),
    dict(name="test4.yml",content="""
- GET: <<42|yi>>
  params:
    yi: fdsqfsdqfdsfdsfdsq
"""),
    dict(name="test5.yml",content="""
- GET: <<42|yi>>
  params:
    yi: fdsqfsdqfd sfdsfdsq
"""),
    dict(name="test6.yml",content="""
- GET: http://x/x
  POST: http://x/x
"""),
    dict(name="test7.yml",content="""
- YOLO: http://x/x

"""),

    dict(name="test8.yml",content="""
- tests:
    - GET: http://x/x
"""),

    dict(name="test9.yml",content="""
- tests
    fsqfdsq: fdsq
    - GET: http://x/x
"""),

    dict(name="test10.yml",content="""
- GET: http://x/x
  params:
    - 1
    - 2
"""),

    dict(name="test11.yml",content="""
- proc:
    - GET: http://x/x
- call: proc
  kiki: toto
"""),

    dict(name="test12.yml",content="""
- GET: http://x/{{v}}
  params:
    v: <<42|kiki>>
"""),

    dict(name="test13.yml",content="""
- GET: http://x/{{v}}
  params:
    v: <<dico.val>>
"""),

    dict(name="test14.yml",content="""
- GET: http://x/{{v}}
  params:
    v: <<dico>>
"""),

    dict(name="test15.yml",content="""
- GET: http://x/{{v}}
  params:
    v: <<dico>>
    dico: <<v>>
"""),


]

def test_1(client):
    x=client( "test1.yml" )
    assert x.code==-1
    assert "ERROR: unknown procedure 'yo'" in x.console

def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0
    assert "Not callable" in x.console

def test_3(client):
    x=client( "test3.yml" )
    assert x.code==0
    assert "Not callable" in x.console

def test_4(client):
    x=client( "test4.yml" )
    assert x.code==-1
    assert "ERROR: Error in execution of method yi" in x.console

def test_5(client):
    x=client( "test5.yml" )
    assert x.code==-1
    assert "ERROR: Error in declaration of method yi" in x.console

def test_6(client):
    x=client( "test6.yml" )
    assert x.code==-1
    assert "ERROR: no action or too many" in x.console

def test_7(client):
    x=client( "test7.yml" )
    assert x.code==-1
    assert "ERROR: no action or too many" in x.console

def test_8(client):
    x=client( "test8.yml" )
    assert x.code==-1
    assert "ERROR: procedure can't be named tests" in x.console

def test_9(client):
    x=client( "test9.yml" )
    assert x.code==-1
    assert "ERROR: YML syntax in" in x.console

def test_10(client):
    x=client( "test10.yml" )
    assert x.code==-1
    assert "ERROR: params is not a dict" in x.console

def test_11(client):
    x=client( "test11.yml" )
    assert x.code==-1
    assert "ERROR: Not a valid entry" in x.console

def test_12(client):
    x=client( "test12.yml" )
    assert x.code==-1
    assert "ERROR: Can't find method" in x.console

def test_13(client):
    x=client( "test13.yml" )
    assert x.code==0        #no more an error

def test_14(client):
    x=client( "test14.yml" )
    assert x.code==0        #no more an error

def test_15(client):
    x=client( "test15.yml" )
    assert x.code==-1
    assert "ERROR: Recursion trouble" in x.console

