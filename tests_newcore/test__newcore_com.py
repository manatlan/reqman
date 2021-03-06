import pytest
import newcore.com

@pytest.mark.asyncio
async def test():
    r=await newcore.com.call("GET","https://httpstat.us/200")
    assert r.status==200
    assert type(r)==newcore.com.Response

    r=await newcore.com.call("GET","https://httpstat.us/200?sleep=2000",timeout=1)
    assert type(r)==newcore.com.ResponseTimeout

    r=await newcore.com.call("GET","fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==newcore.com.ResponseInvalid

    r=await newcore.com.call("GET","http://fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==newcore.com.ResponseUnreachable


