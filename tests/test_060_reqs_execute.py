import pytest,reqman

MOCK={"https://www.manatlan.com":(200,"ok")}

def test_static(Reqs):
    y="""
- yo:
    - yo2:
        - GET: https://www.manatlan.com
          foreach:
            - c: 10
            - c: 20
    - call: yo2
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
    l.execute( MOCK )

def test_dynamic(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<liste>>
"""
    env=dict(liste=[dict(a=1),dict(a=2)])
    l=Reqs(y,env)
    assert len(l) == 1
    l.execute( MOCK )



def test_dynamic_bad(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: "nope"
"""
    env=dict(liste=[dict(a=1),dict(a=2)])
    
    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad2(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<unknown>>
"""
    l=Reqs(y)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad3(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp="kkoo")

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad33(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp=None)

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad333(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp=False)

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad333(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp=42)

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad4(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp=dict(a=2))

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )

def test_dynamic_bad5(Reqs):
    y="""
  - GET: https://www.manatlan.com
    foreach: <<nimp>>
"""
    env=dict(nimp=list("abc"))

    l=Reqs(y,env)
    assert len(l) == 1
    
    with pytest.raises(reqman.RMException):
      l.execute( MOCK )




