import pytest,reqman


def test_simplest(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers:
    jo: hello
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.Req
    assert l[0].headers == {'jo': 'hello'}

def test_simplest2(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
      headers:
        jo: hello
- call: yo
  headers:
    jo: hello2
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup    
    assert l[0].reqs[0].headers == {'jo': 'hello2'}

def test_headers_as_list_and_tests_as_dict(Reqs): #bad practice
    y="""
- yo:
    - GET: https://www.manatlan.com
      headers:
        - jo: hello
      tests:
        status: 200
- call: yo
  headers:
    - jo: hello2
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup    
    assert l[0].reqs[0].headers == {'jo': 'hello2'}

def test_empty(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers:
"""
    l=Reqs(y)
    assert len(l) == 1
    assert l[0].headers == {}

def test_bad(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers: "nimp"
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)



def test_2simplest(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers:
    jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 1

def test_2simplest2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
- call: proc
  headers:
    jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 1

def test_2simplest3(Reqs): # bad header's ext, but not called -> forget
    y="""
- proc:
    - GET: https://www.manatlan.com
      Headers:
         jo: fsdgfdsgfds
"""
    l=Reqs(y)
    assert len(l) == 0



def test_2bad(Reqs):
    y="""
- GET: https://www.manatlan.com
  Headers:
    jo: fsdgfdsgfds
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_2bad2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
- call: proc
  Headers:
    jo: fsdgfdsgfds
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_2bad3(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
      Headers:
          jo: fsdgfdsgfds
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_2bad4(Reqs):
    y="""
- proc:
    - YO: https://www.manatlan.com
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_2bad_actionExt1(Reqs):
    y="""
- GET: https://www.manatlan.com
  headers: "yolo"
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_2bad_actionExt2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
      headers: "yolo"
- call: proc
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_header_override_remove(Reqs):
    y="""
- yo:
    - GET: https://www.manatlan.com
      headers:
        jo: hello
- call: yo
  headers:
    jo: null
"""
    l=Reqs(y)
    assert len(l) == 1
    assert type(l[0]) is reqman.ReqGroup    
    assert l[0].reqs[0].headers ==  {'jo': None}  # before execution

    ll=l.execute( {"https://www.manatlan.com":(200,"ok")})
    assert len(ll) == 1
    assert ll[0].inHeaders=={}
