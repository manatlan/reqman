#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/t" : (200,"ne pas être là!")
}

FILES=[
    dict(name="test1.yml",content="""
- GET: http://x/t
  doc: à boïng
  tests:
    - status: 200
    - content: être
"""),
    dict(name="test2.yml",content="""
- GET: http://x/t
  doc: à boïng
  tests:
    - status: 200
    - content: être
""".encode("utf8").decode("cp1252")),
]

def test_html_output(client):
    x=client( "test1.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2

    assert 'content contains "être"' in x.html
    assert 'à boïng' in x.html
    assert '-> MOCK 200' in x.html

    # with open("/home/manatlan/aeff.html","w+") as fid:
    #     fid.write(x.html)

def test_html_output2(client):
    x=client( "test2.yml" )
    # with open("/home/manatlan/aeff.html","w+") as fid:
    #     fid.write(x.html)
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2

    assert 'content contains "être"' in x.html
    assert 'à boïng' in x.html
    assert '-> MOCK 200' in x.html



