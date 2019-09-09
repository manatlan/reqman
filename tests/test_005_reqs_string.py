import pytest,reqman,pickle

def test_reqs_pickable(Reqs):
    y="""
GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 1

    r=l[0]
    rr=pickle.loads(pickle.dumps(r))
    assert rr.method == r.method
    assert rr.path == r.path
    assert rr.body == r.body
    assert rr.doc == r.doc
    assert rr.saves == r.saves
    assert rr.headers == r.headers
    # assert rr.parent == r.parent

    ll=pickle.loads(pickle.dumps(l))
    assert len(ll)==len(l)
    assert ll[0].path==l[0].path

def test_simplest(Reqs):
    y="""
GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 1

def test_simplest2(Reqs):
    y="""
- GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 1

def test_bad_2verbs(Reqs):
    y="""
    - GET: https://www.manatlan.com
      POST: https://www.manatlan.com
    """
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)


def test_bad(Reqs):
    y="""hello"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad2(Reqs):
    y="""
- GET: https://www.manatlan.com
- hhjfdhhfdjs
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad3(Reqs):
    y="""
- FUCK: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad4(Reqs):
    y="""
- GET: 
    nimp: nimp
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)
        
def test_bad5(Reqs):
    y="""
- GET:
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad6(Reqs):
    y="""
- GET: hgfdhgfd
jo: malformed
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad7(Reqs):
    y="""
ffdsqfds
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)


def test_empty(Reqs):
    l=Reqs("")
    assert len(l) == 0