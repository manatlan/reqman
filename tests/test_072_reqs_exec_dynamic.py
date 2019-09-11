import pytest,json

mock={
    "https://www.manatlan.com/hello":(200,"ok"),
}

def test_normal(Reqs):
    y="""
- GET: https://www.manatlan.com/<<v>>
  params:
    v: return "hello"
  tests:
    - status: 200
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( mock )
    assert all(ll[0].tests)


def test_bytes(Reqs):
    y="""
- GET: https://www.manatlan.com/<<bytes|str>>
  params:
    bytes: return b"hello"
    str: return x.decode()
  tests:
    - status: 200
"""
    l=Reqs(y)
    assert len(l) == 1
    ll=l.execute( mock )
    assert all(ll[0].tests)
