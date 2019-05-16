#!/usr/bin/python
# -*- coding: utf-8 -*-



SERVER={
    "/mypingpong" : lambda q: (200, "ok" if q.body==bytes( list(range(255,0,-1)) ) else "ko")
}

FILES=[
    dict(name="test1.yml",content="""
- POST: http://x/mypingpong
  body: <<|bytes>>
  params:
     bytes: |
        return bytes( list(range(255,0,-1)) )
  tests:
    - status: 200
    - content: "ok"
"""),
]

def test_1(client):
    x=client( "test1.yml" )
    # assert x.code==0
    with open("/home/manatlan/aeff.html","w+") as fid:
        fid.write( x.html )
