#!/usr/bin/python
# -*- coding: utf-8 -*-

FILES=[
    dict(name="jim.yml",content="""
  - sortDirection:
    - GET: http://jim/<<name>>-<<direction>>
      doc: "[[<<name>>-<<direction>>]]"
      tests:
         - status: 404
  
  - sortName: 
    - call: sortDirection
      foreach:
        - direction: A
        - direction: D
    
  - call: sortName
    foreach:
      - name : NAME
      - name : AGE
"""),
]

def test_1(client):
    x=client( "jim.yml" )
    assert "[[NAME-D]]" in x.html
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total