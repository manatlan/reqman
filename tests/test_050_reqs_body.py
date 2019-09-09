import pytest,reqman


def test_empty(Reqs):
    y="""
- POST: https://www.manatlan.com
  body:
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body is None

def test_null(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: null
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body is None

def test_string(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: "hello"
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == "hello"

def test_dict(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: 
    a: 12
    b: 13
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == {'a': 12, 'b': 13}

def test_list(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: 
    - line1
    - line2
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == ["line1","line2"]

def test_bool(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: true
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body is True

def test_number(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: 42
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == 42

def test_float(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: 3.14
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == 3.14

def test_tuple_is_string(Reqs):
    y="""
- POST: https://www.manatlan.com
  body: (12,34)
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].body == '(12,34)'


# def test_bad(Reqs):
#     y="""
# - GET: https://www.manatlan.com
#   headers: "nimp"
# """
#     with pytest.raises(reqman.RMFormatException):
#         Reqs(y)