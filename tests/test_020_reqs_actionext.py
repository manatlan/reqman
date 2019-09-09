import pytest,reqman

#TODO: a ventiler dans les autres

def test_simplest(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers:
    jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 1

def test_simplest2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
- call: proc
  headers:
    jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 1

def test_simplest3(Reqs): # bad header's ext, but not called -> forget
    y="""
- proc:
    - GET: https://www.manatlan.com
      Headers:
         jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 0



def test_bad(Reqs):
    y="""
- GET: https://www.manatlan.com
  Headers:
    jo: fsdgfdsgfds
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
- call: proc
  Headers:
    jo: fsdgfdsgfds
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad3(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
      Headers:
          jo: fsdgfdsgfds
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad4(Reqs):
    y="""
- proc:
    - YO: https://www.manatlan.com
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad_actionExt1(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers: "yolo"
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_bad_actionExt2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
      headers: "yolo"
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)
