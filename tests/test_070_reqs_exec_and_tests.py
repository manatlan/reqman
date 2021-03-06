import pytest,reqman,json

MOCK={"https://www.manatlan.com/IAmThePath":(200,"ok")}

def test_simplest_ko(Reqs):
    y="""
POST: https://www.manatlan.com/<<path_jo>>
headers:
    jo: <<header_jo>>
body: Hello <<val_jo>>
tests:
    - status: 404
"""
    l=Reqs(y)
    assert len(l) == 1
    ll= l.execute(MOCK)
    assert ll[0].url == "https://www.manatlan.com/<<path_jo>>"
    assert ll[0].inHeaders == {"jo": "<<header_jo>>"}
    # print(ll[0].body)
    # assert ll[0].body == b"Hello <<val_jo>>"
    assert ll[0].status==None
    assert not any(ll[0].tests)

def test_simplest_ok(Reqs):
    y="""
POST: https://www.manatlan.com/<<path_jo>>
headers:
    jo: <<header_jo>>
body: Hello <<val_jo>>
tests:
    - status: 200
    - content: ok
"""
    env=dict(
        path_jo="IAmThePath",
        header_jo="IAmTheHeader",
        val_jo="IAmTheContent",
    )
    l=Reqs(y,env)
    assert len(l) == 1
    ll= l.execute(MOCK)
    assert ll[0].url == "https://www.manatlan.com/IAmThePath"
    assert ll[0].inHeaders == {"jo": "IAmTheHeader"}
    assert ll[0].body == b"Hello IAmTheContent"
    assert any(ll[0].tests)

def test_save(Reqs):
    y="""
- GET: /a
  save: r
- GET: /b
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"b"),"/b":(200,"ok")} )
    assert len(ll) == 2

    assert ll[0].url == "/a"
    assert ll[1].url == "/b"

    assert l.env["r"]=="b"

def test_tests(Reqs):
    y="""
- GET: /a
  tests:
    - status: 200
    - content: ok
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/a":(200,"ok")} )
    assert len(ll) == 1
    assert all( ll[0].tests )

def test_tests_json(Reqs):
    y="""
- GET: /a
  tests:
    - status: 200
    - status: "200"
    - json.v: 42
    - json.v: "42"
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=42)))} )
    assert len(ll) == 1
    assert all( ll[0].tests )

def test_tests_json(Reqs):
    y="""
- GET: /a
  tests:
    - json.v: <<v1>>
    - json.v: <<v2>>
  params:
    v1: 42
    v2: "42"
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=42)))} )
    assert len(ll) == 1
    assert all( ll[0].tests )

def test_tests_json2(Reqs):
    y="""
- proc:
    - GET: /a
      tests:
        - json.v: <<v1>>
        - json.v: <<v2>>
- call: proc
  params:
    v1: 43
    v2: "43"
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=43)))} )
    assert len(ll) == 1
    assert all( ll[0].tests )

def test_foreach_dynamic(Reqs):
    y="""
- proc:
    - GET: /a
      tests:
        - json.v: <<v1>>
        - json.v: <<v2>>
        - status: .!=111
        - status: .>100
        - status: .>=100
        - status: .<300
        - status: .<=300
        - status: 200
        - status: .=200
        - status: .==200
- call: proc
  foreach: <<dynlist>>
  params:
    v1: 43
    v2: "43"
"""
    l=Reqs(y, dict(dynlist=[{"i":1},{"i":2}])  )
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=43)))} )
    assert len(ll) == 2
    assert all( ll[0].tests )
    assert all( ll[1].tests )

def test_foreach_static_from_main(Reqs):
    y="""
- proc:
    - GET: /a
      tests:
        - json.v: <<v1>>
        - json.v: <<v2>>
- call: proc
  foreach: <<staticlist>>
  params:
    v1: 43
    v2: "43"
    staticlist:
        - i: 1
        - i: 2
"""
    l=Reqs(y )
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=43)))} )
    assert len(ll) == 2
    assert all( ll[0].tests )
    assert all( ll[1].tests )

def test_foreach_static_inside_proc(Reqs):
    y="""
- proc:
    - GET: /a
      foreach: <<staticlist>>
- call: proc
  params:
    staticlist:
        - i: 1
        - i: 2
"""
    l=Reqs(y )
    assert len(l) == 1
    ll=l.execute( {"/a":(200,json.dumps(dict(v=43)))} )
    assert len(ll) == 2

def test_check_hermetic_scope(Reqs):
    y="""
- proc:
    - GET: <<v>>
- call: proc
  params:
    v: /a

- proc2:
    - GET: <<vv>>
- call: proc2
  params:
    vv: /a
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"ok")} )
    assert len(ll) == 2
    assert ll[0].scope=={'v': '/a'}
    assert ll[1].scope=={'vv': '/a'}


def test_check_hermetic_scope2(Reqs):
    y="""
- proc:
    - GET: <<v>>
      params:
        p: 1

- call: proc
  params:
    v: /a

- call: proc
  params:
    vv: /a
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"ok")} )
    assert len(ll) == 2
    assert ll[0].scope=={'v': '/a', 'p': 1}
    assert ll[1].scope=={'vv': '/a',  'p': 1}

def test_check_hermetic_scope3(Reqs):
    y="""
- proc:
    - GET: <<v>>
      params:
        p: 1

- call: proc
  foreach:
    - v: /a

- call: proc
  foreach:
    - vv: /a
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"ok")} )
    assert len(ll) == 2
    assert ll[0].scope=={'v': '/a', 'p': 1}
    assert ll[1].scope=={'vv': '/a',  'p': 1}

def test_check_hermetic_scope4(Reqs):
    y="""
- proc:
    - GET: <<v>>
      params:
        p: 1
    - GET: <<v>>
      params:
        p: 2
      foreach:
        - i: 1
        - i: 2
- call: proc
  foreach:
    - v: /a

- call: proc
  foreach:
    - v: /b
"""
    l=Reqs(y)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"ok"),"/b":(200,"ok")} )
    assert len(ll) == 6
    assert ll[0].scope=={'p': 1, 'v': '/a'}
    assert ll[1].scope=={'p': 2, 'v': '/a', 'i': 1}
    assert ll[2].scope=={'p': 2, 'v': '/a', 'i': 2}
    assert ll[3].scope=={'p': 1, 'v': '/b'}
    assert ll[4].scope=={'p': 2, 'v': '/b', 'i': 1}
    assert ll[5].scope=={'p': 2, 'v': '/b', 'i': 2}

    l=Reqs(y,trace=1)
    assert len(l) == 2
    ll=l.execute( {"/a":(200,"ok"),"/b":(200,"ok")} )
