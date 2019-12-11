import pytest,reqman,json
import reqman, asyncio, pytest

@pytest.mark.asyncio
async def test_nimp():

    
    conf="""
BEGIN:
    - GET: /check
      tests:
        - status: 200

proc1: return x*"a"

val_bb: bb
v: 2

dua:
    root: http://machinedua.com

"""
    r=reqman.Reqman(conf)

    assert r.switches==[("dua","http://machinedua.com")]

    r.add("""
- call: BEGIN
- GET: /<<i>>
  tests:
    - status: 200
  foreach:
    - i: 1
    - i: 2
""")

    r.add("""
- GET: /<<v|proc1>>
  tests:
    - status: 200
- POST: /<<v|proc2>>
  tests:
    - status: 200
  params:
    proc2: return x*"a"
- PUT: /<<val_bb>>
  tests:
    - status: 200
""")
    mock={"/":(200,"ok"),"/bb":(200,"ok"),"/aa":(200,"ok"),"/check":(200,"ok"),"/1":(200,"ok"),"/2":(200,"ok")}
    rr=await r.asyncExecute( paralleliz=True, http=mock )
    assert rr.code==0

        
    ll=await r.asyncExecute( paralleliz=False, http=mock )
    assert rr.code==0
