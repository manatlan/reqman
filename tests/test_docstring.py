import reqman
from io import StringIO
def test_1():
    y="""
- GET: /
"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc is None

def test_2():
    y="""
- GET: /
  doc: just for fun
"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc == "just for fun"

def test_3():
    y="""
- GET: /
  doc: x <<msg>> x
  params:
    msg: kiki

"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc == "x kiki x" # replace in docstring !!!

def test_33():
    y="""
- GET: /
  doc: x <<msg>> x
  params:
    msg: 
        int: 42
        str: "yo"
        ll:
            - 1
            - "2"

"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc == """x {"int": 42, "str": "yo", "ll": [1, "2"]} x""" # replace in docstring !!!


def test_34():
    y="""
- GET: /
  doc: x <<msg>> x
"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc == """x <<msg>> x""" 


def test_4():
    y="""
- proc:
    - GET: /
      doc: x<<msg>>x

- call: proc
  foreach:
    - msg: kiki1
    - msg: kiki2

"""
    l=reqman.Reqs(StringIO(y))
    assert len(l)==2
    assert l[0].doc == "xkiki1x" # no replace in docstring
    assert l[1].doc == "xkiki2x" # no replace in docstring
