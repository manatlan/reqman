#!/usr/bin/python
# -*- coding: utf-8 -*-



SERVER={
    "/1" : ( 200, "dsq"),
    "/2" : ( 200, "dsq"),
    "/getalist" : ( 200, [1,2,3]),
    "/geta" : ( 200, "dsq"),
}

FILES=[
    dict(name="test.yml",content="""
- GET: http://xxx/<<v>>
  tests:
    - status: 200
    - content: dsq
  foreach: <<a_liste>>
  params:
    a_liste:
        - v: 1
        - v: 2
"""),
    dict(name="test2.yml",content="""
-   GET: http://xxx/<<v>>
    tests:
        - status: 200
        - content: dsq
    foreach: <<2|mkliste>>
    params:
        mkliste: return x * [ {"v":1} ]
"""),
    dict(name="test3.yml",content="""
-   GET: http://xxx/<<v>>
    tests:
        - status: 200
        - content: dsq
    foreach: <<bad_type>>
    params:
        bad_type:
            v: 1
            v: 2
"""),
    dict(name="test4.yml",content="""
- GET: http://xxx/<<v>>
  tests:
    - status: 200
    - content: dsq
  foreach: <<a_liste>>
  params:
    a_liste:
        - v: 1
        - <<vvv>>
    vvv:
        v: 2
"""),


    dict(name="test_l.yml",content="""
- GET: http://getalist
  tests:
    - status: 200
  save: l
- GET: http://geta
  foreach: <<l>>
"""),
]

def test_1(client):
    x=client( "test.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2
def test_4(client):
    x=client( "test4.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2
def test_2(client):
    x=client( "test2.yml" )
    assert x.code==0 # all ok
    assert x.inproc.ok == x.inproc.total == 4
    assert len(x.inproc.reqs[0])==2

def test_3(client):
    x=client( "test3.yml" )
    assert x.code==-1

# def test_dyna_list(client):
#     x=client( "test_l.yml" )
#     assert x.code==0
