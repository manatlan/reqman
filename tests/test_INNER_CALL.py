import os
import reqman,io

async def test_innercall():
    f="""- GET: http://example.com/t"""
    x=await reqman.testContent( f )
    assert x.code==0
