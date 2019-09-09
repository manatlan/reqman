import pytest,reqman

# same as 045
# same as 045
# same as 045
# same as 045, but with dynamic param (python param)

def test_complexe(Reqs): # ensure now is executed before upper
    y="""
- POST: /
  body: <<fichier|upper>>
  params:
    upper: return x.upper()
    now: |
      return "xxx"
    fichier: www<<now>>www
"""
    l=Reqs(y)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe1(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
      params:
        upper: return x.upper()
        now: return "xxx"
        fichier: www<<now>>www
- call: PROC
"""
    l=Reqs(y)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe2(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
      params:
        upper: return x.upper()
        fichier: www<<now>>www
- call: PROC
  params:
    now: return "xxx"
"""
    l=Reqs(y,trace=True)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe3(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
      params:
        fichier: www<<now>>www
- call: PROC
  params:
    now: return "xxx"
    upper: return x.upper()
"""
    l=Reqs(y)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe4(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
      params:
        upper: return x.upper()
- call: PROC
  params:
    fichier: www<<now>>www
    now: return "xxx"
"""
    l=Reqs(y)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe5(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
      params:
        now: return "xxx"
- call: PROC
  params:
    fichier: www<<now>>www
    upper: return x.upper()
"""
    l=Reqs(y)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

def test_complexe6(Reqs): # ensure now is executed before upper
    y="""
- PROC:
    - POST: /
      body: <<fichier|upper>>
- call: PROC
  params:
    fichier: www<<now>>www
    now: return "xxx"
    upper: return x.upper()
"""
    l=Reqs(y,trace=True)
    assert len(l) == 1

    ll=l.execute( {"/" : (200,"ok")} ) # reqman.RMException: Can't find method 'NOW'
    assert ll[0].body == b"WWWXXXWWW" 

