#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import client


SERVER={
    "/t" : (200,"ne pas être là!"),
    "/x" : (200,"<root><a>Yolo</a></root>"),
}

FILES=[
    dict(name="test_utf8.yml",content="""
- GET: http://x/t
  doc: à boïng
  tests:
    - status: 200
    - content: être
"""),
    dict(name="test_cp1252.yml",content="""
- GET: http://x/t
  doc: à boïng
  tests:
    - status: 200
    - content: être
""".encode("utf8").decode("cp1252")),
    dict(name="test_xml.yml",content="""
- GET: http://x/x
  tests:
    - status: 200
    - content: <a>Yolo</a>
""")
]

def test_html_output(client):
    x=client( "test_utf8.yml" )
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2

    assert 'content contains "être"' in x.html
    assert 'à boïng' in x.html
    assert '-> MOCK 200' in x.html

    # with open("/home/manatlan/aeff.html","w+") as fid:
    #     fid.write(x.html)

def test_html_output2(client):
    x=client( "test_cp1252.yml" )
    # with open("/home/manatlan/aeff.html","w+") as fid:
    #     fid.write(x.html)
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2

    assert 'content contains "être"' in x.html
    assert 'à boïng' in x.html
    assert '-> MOCK 200' in x.html


def test_html_output3(client):
    x=client( "test_xml.yml" )
    # with open("/home/manatlan/aeff.html","w+") as fid:
    #     fid.write(x.html)
    assert x.code==0 # 0 error
    assert x.inproc.total==2
    assert x.inproc.ok==2

    assert '&lt;root&gt;' in x.html,"xml has not been escaped !"
