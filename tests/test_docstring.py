from context import reqman
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
  doc: x<<msg>>x
  params:
    msg: kiki

"""
    l=reqman.Reqs(StringIO(y))
    assert l[0].doc == "x<<msg>>x" # no replace in docstring

def test_4():
    y="""
- proc:
    GET: /
    doc: x<<msg>>x

- call: proc
  foreach:
    - msg: kiki1
    - msg: kiki2

"""
    l=reqman.Reqs(StringIO(y))
    assert len(l)==2
    assert l[0].doc == "x<<msg>>x" # no replace in docstring
    assert l[1].doc == "x<<msg>>x" # no replace in docstring
