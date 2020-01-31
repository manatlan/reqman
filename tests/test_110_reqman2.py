import pytest,reqman,json
import reqman, asyncio, pytest


MOCK={
        "/first":(200,"path"),
        "/path/a":(200,"ok"),

        "/value":(200,"ok"),
        "/ok":(200,"ok"),
    }

CONF="""
BEGIN:
    - GET: /first
      tests:
        - status: 200
      save: token

headers:
  test: This is a global header
"""

@pytest.mark.asyncio
async def test_hermetic_env_paralleliz():
    
    r=reqman.Reqman(CONF)
    r.outputConsole = reqman.OutputConsole.FULL

    r.add("""
- GET: /<<token>>/a
  tests:
    - status: 200

- GET: /<<suite>>
  tests:
    - status: 404

- proc:
    - proc2:
        - GET: /value
          tests:
            - status: 200
          save: suite
        
        - GET: /<<suite>>
          tests:
            - status: 200
    - call: proc2

- call: proc

- GET: /<<suite>>
  tests:
    - status: 200

""")

    rr=await r.asyncExecute( paralleliz=True, http=MOCK )
    assert rr.code==1 #1 error coz the 404 test is non playable

@pytest.mark.asyncio
async def test_hermetic_env():
    
    r=reqman.Reqman(CONF)
    r.outputConsole = reqman.OutputConsole.FULL

    r.add("""
- GET: /<<token>>/a
  tests:
    - status: 200

- GET: /<<suite>>
  tests:
    - status: 404

- proc:
    - proc2:
        - GET: /value
          tests:
            - status: 200
          save: suite
        
        - GET: /<<suite>>
          tests:
            - status: 200
    - call: proc2

- call: proc

- GET: /<<suite>>
  tests:
    - status: 200

""")

    rr=await r.asyncExecute( paralleliz=False, http=MOCK )
    assert rr.code==1 #1 error coz the 404 test is non playable
