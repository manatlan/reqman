import pytest,os
from src import reqman

@pytest.mark.skipif(os.getenv("CI") == "true", reason="No internet on CI")
@pytest.mark.asyncio
async def test_real_http_call():
    reqman.com.init()

    r=await reqman.com.call("GET","https://tools-httpstatus.pickup-services.com/200")
    assert r.status==200
    assert type(r)==reqman.com.Response

    r=await reqman.com.call("GET","fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==reqman.com.ResponseInvalid

    r=await reqman.com.call("GET","http://fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==reqman.com.ResponseUnreachable

@pytest.mark.skipif(os.getenv("CI") == "true", reason="No internet on CI")
@pytest.mark.asyncio
async def test_real_http_call_timeout():
    reqman.com.init()

    r=await reqman.com.call("GET","https://tools-httpstatus.pickup-services.com/200?sleep=1000",timeout=1)
    assert type(r)==reqman.com.ResponseTimeout


def test_simu_call():
    mock={
        "/":(200,"ok"),
        "/bytes":(200,b"ok"),
        "/cp1252":(200,"oké".encode().decode("cp1252")),    #body is str
        "/utf8":(200,"oké"),                                #body is str
        "/fct": lambda method, url, body, headers: (200,"ok"),
        "/fct_h": lambda method, url, body, headers: (200,"ok",headers),
    }

    r=reqman.com.call_simulation( mock ,"GET","/" )
    assert r.status==200
    assert r.content == b"ok"

    r=reqman.com.call_simulation( mock ,"GET","/bytes" )
    assert r.status==200
    assert r.content == b"ok"

    r=reqman.com.call_simulation( mock ,"GET","/cp1252" )
    assert r.status==200
    assert r.content.decode() == "oké"

    r=reqman.com.call_simulation( mock ,"GET","/utf8" )
    assert r.status==200
    assert r.content.decode() == "oké"

    r=reqman.com.call_simulation( mock ,"GET","/fct" )
    assert r.status==200
    assert r.content == b"ok"

    r=reqman.com.call_simulation( mock ,"GET","/fct_h",headers=dict(hello="hello") )
    assert r.status==200
    assert r.content == b"ok"
    assert r.headers["hello"] == "hello"
