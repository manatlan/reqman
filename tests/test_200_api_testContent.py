import reqman, asyncio, pytest

@pytest.mark.asyncio
async def test():
    yml="""
- GET: /a
  tests:
    status: 200
    content: ok
"""
    env={}
    mock={"/a":(200,"ok")}

    r= await reqman.testContent(yml,env,mock) 

    assert r.html
    assert r.code==0
    assert r.ok==2
    assert r.total==2
