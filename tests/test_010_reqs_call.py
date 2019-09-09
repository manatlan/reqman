import pytest,reqman


def test_simplest(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call: yo
"""
    l=Reqs(y)
    assert len(l) == 1

def test_simplest1(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call:
    - yo
"""
    l=Reqs(y)
    assert len(l) == 1

def test_simplest1(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call:
    - yo
    - yo
"""
    l=Reqs(y)
    assert len(l) == 2

def test_simplest2(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call: yo
- GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 2

def test_simplest3(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
    - GET: https://www.manatlan.com
- call: yo
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup

def test_simplest4(Reqs):
    y="""
- yo2:
    - GET: https://www.manatlan.com
- yo:
    - GET: https://www.manatlan.com
    - call: yo2
- call: yo
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup

def test_simplest5(Reqs):
    y="""
- yo:
    - yo2:
        - GET: https://www.manatlan.com
    - GET: https://www.manatlan.com
    - call: yo2
- call: yo
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup


def test_empty(Reqs):
    y="""
- yo2:
    - GET: https://www.manatlan.com
    - GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 0

def test_empty2(Reqs):
    y="""
- yo2:
    - GET: https://www.manatlan.com
    - "shit happens here"
"""
    l=Reqs(y)
    assert len(l) == 0    

def test_bad_2action(Reqs):
    y="""
    - jo:
        - GET: https://www.manatlan.com
    - GET: https://www.manatlan.com
      call: jo
    """
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)
        
def test_bad(Reqs):
    y="""
- call: yo
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad2(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
    - "shit happens here"
- call: yo
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad3(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- yo:
    - GET: https://www.manatlan.com
- call: yo
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad4(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call: 
    yo: yo
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad5(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
- call: 
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)
