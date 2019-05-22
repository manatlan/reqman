import os
import reqman,io

def test_innercall():
    f="""- GET: http://example.com/t"""
    x=reqman.testContent( f )
    assert x.code==0
