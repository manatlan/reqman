import pytest,reqman


def test_simplest(Reqs):
    y="""
- GET: https://www.manatlan.com
  foreach:
    - a: 12
    - a: 20
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup

def test_simplest2(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call: yo
  foreach:
        - a: 12
        - a: 20
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup

# def test_print_reqs(Reqs):
#     y="""
# - GET: /<<i>>
#   tests:
#     - status: 200
#   foreach:
#     - i: 1
#     - i: 2
# """
#     l=Reqs(y,name="mon_fichier.yml")
#     assert len(l) == 1
#     out="""Reqs's Name: mon_fichier.yml
# <ReqGroup foreach:[{'i': 1}, {'i': 2}] scope:{}>
#   <Req GET: /<<i>>>
#   	tests: [{'status': 200}]"""
#     assert repr(l) == out
#     l.execute( {"/1":(200,"ok"),"/2":(200,"ok")} )
#     assert repr(l) == out

def test_simplest3(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
      foreach:
        - b: 10
        - b: 20
- call: yo
  foreach:
        - a: 10
        - a: 20
"""
    l=Reqs(y)
    assert len(l) == 1
    # assert l[-1].params == {'b': 20, 'a': 20}


def test_empty(Reqs):
    y="""
- GET: https://www.manatlan.com
  foreach: #does nothing
"""
    l=Reqs(y)
    assert len(l) == 1

def test_bad(Reqs):
    y="""
- GET: https://www.manatlan.com
  foreach:
    a: 12
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)