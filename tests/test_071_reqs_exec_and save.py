import pytest,reqman,json

mock={
    "/start" : (200,json.dumps(dict(route=dict(second="next"),nb=42))),
    "/go/next" : (200,"ok"),
}


def test_save(Reqs):
    y="""
- GET: /a
  save: r
- GET: /<<r>>
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"b"),"/b":(200,"ok")} )
    assert len(ll) == 2

    assert ll[0].url == "/a"
    assert ll[1].url == "/b"

def test_save_new(Reqs):
    y="""
- GET: /a
  save:
    r: <<content>>
- GET: /<<r>>

- GET: /a
  save:
    r: <<status>>
- GET: /<<r>>


- GET: /j
  save:
    r: <<json.v>>
- GET: /<<r>>

"""
    l=Reqs(y)
    assert len(l) == 6
    ll=l.execute( {"/a":(200,"b"),"/b":(200,"ok"),"/200":(200,"ok"),"/j":(200,json.dumps({"v":"b"}))} )
    assert len(ll) == 6

    assert ll[0].url == "/a"
    assert ll[1].url == "/b"
    
    assert ll[2].url == "/a"
    assert ll[3].url == "/200"

    assert ll[4].url == "/j"
    assert ll[5].url == "/b"

def test_save_new_VIA_CALL(Reqs):
    y="""
- PROC:
    - GET: /a
      save:
        r: <<content>>
    - GET: /<<r>>

    - GET: /a
      save:
        r: <<status>>
    - GET: /<<r>>


    - GET: /j
      save:
        r: <<json.v>>
    - GET: /<<r>>

- call: PROC
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/a":(200,"b"),"/b":(200,"ok"),"/200":(200,"ok"),"/j":(200,json.dumps({"v":"b"}))} )
    assert len(ll) == 6

    assert ll[0].url == "/a"
    assert ll[1].url == "/b"
    
    assert ll[2].url == "/a"
    assert ll[3].url == "/200"

    assert ll[4].url == "/j"
    assert ll[5].url == "/b"

def test_save_1(Reqs):
    env=reqman.Env( """
PROC:
    - GET: /<<first>>
      doc: fonction commune
      tests:
        - status: 200
""")

    y="""
- call: PROC
  params:
    first: start
  save: data
- POST: /go/<<data.route.second>>
  tests:
    - status: 200
    - content: ok
"""

    
    l=Reqs(y,env)    
    ll=l.execute( mock )
    assert len(ll)==2
    assert all(ll[0].tests)
    assert all(ll[1].tests)


def test_save_2(Reqs):
    env=reqman.Env( """
PROC:
    - GET: /<<first>>
      doc: fonction commune
      tests:
        - status: 200
""")
    y2="""
- context:
    - call: PROC
      params:
        first: start
      save: 
        redirige: <<json.route.second>>

    - POST: /go/<<redirige>>
      tests:
        - status: 200
        - content: ok

- call: context
"""

    l=Reqs(y2,env,trace=True)    
    ll=l.execute( mock )
    assert len(ll)==2
    assert all(ll[0].tests)
    assert all(ll[1].tests)
