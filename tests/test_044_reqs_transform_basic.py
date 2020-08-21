import pytest,reqman


def test_simplest(Reqs):
    y="""
- GET: /<<v|upper>>
  params:
    v: hello
    upper: return x.upper()
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/HELLO" : (200,"ok")} )
    assert ll[0].url == "/HELLO"

def test_simplest_chaining(Reqs):
    y="""
- GET: /<<v|upper|lower>>
  params:
    v: Hello
    upper: return x.upper()
    lower: return x.lower()
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( {"/hello" : (200,"ok")} )
    assert ll[0].url == "/hello"

def test_simplest_transciant(Reqs):
    y="""
- GET: /<<param>>
  params:
    param: <<v|upper>>
    v: hello
    upper: return x.upper()
"""
    l=Reqs(y,trace=True)
    assert len(l) == 1
    ll=l.execute( {"/HELLO" : (200,"ok")} )
#     assert ll[0].url == "/HELLO"


def test_pass_object_to_method(Reqs):
    y="""
- GET: /<<param>>
  params:
    param: <<data|getVal>>
    data:
        value: "hello"
        nimp: 42
    getVal: return x.get("value")
"""
    l=Reqs(y,trace=True)
    ll=l.execute( {"/hello" : (200,"ok")} )
    assert ll[0].url == "/hello"


def test_pass_object_to_method_jwt(Reqs):
    y="""
- GET: /hello
  headers:
    Authorization: Bearer <<data|createJwt>>
  params:
    data:
        value: "hello"
        nimp: 42
    createJwt: |
        import jwt
        return jwt.encode(data,"").decode()
"""
    l=Reqs(y,trace=True)
    ll=l.execute( {"/hello" : (200,"ok")} )
    assert ll[0].url == "/hello"

