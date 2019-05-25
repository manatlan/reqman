import asyncio
import reqman

def test_innercall():
    f="""- GET: http://example.com/t"""
    x=asyncio.run( reqman.testContent( f ) )
    assert x.code==0
