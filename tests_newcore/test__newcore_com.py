import pytest
import newcore.com

@pytest.mark.asyncio
async def test_real_http_call():
    r=await newcore.com.call("GET","https://httpstat.us/200")
    assert r.status==200
    assert type(r)==newcore.com.Response

    r=await newcore.com.call("GET","https://httpstat.us/200?sleep=2000",timeout=1)
    assert type(r)==newcore.com.ResponseTimeout

    r=await newcore.com.call("GET","fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==newcore.com.ResponseInvalid

    r=await newcore.com.call("GET","http://fgsdjghfdsgfsdhhgfdjks.com")
    assert type(r)==newcore.com.ResponseUnreachable


def test_simu_call():
    mock={
        "/":(200,"ok"),
        "/bytes":(200,b"ok"),
        "/cp1252":(200,"oké".encode().decode("cp1252")),    #body is str
        "/utf8":(200,"oké"),                                #body is str
        "/fct": lambda method, url, body, headers: (200,"ok"),
        "/fct_h": lambda method, url, body, headers: (200,"ok",headers),
    }

    r=newcore.com.call_simulation( mock ,"GET","/" )
    assert r.status==200
    assert r.content == b"ok"

    r=newcore.com.call_simulation( mock ,"GET","/bytes" )
    assert r.status==200
    assert r.content == b"ok"

    r=newcore.com.call_simulation( mock ,"GET","/cp1252" )
    assert r.status==200
    assert r.content.decode() == "oké"

    r=newcore.com.call_simulation( mock ,"GET","/utf8" )
    assert r.status==200
    assert r.content.decode() == "oké"

    r=newcore.com.call_simulation( mock ,"GET","/fct" )
    assert r.status==200
    assert r.content == b"ok"

    r=newcore.com.call_simulation( mock ,"GET","/fct_h",headers=dict(hello="hello") )
    assert r.status==200
    assert r.content == b"ok"
    assert r.headers["hello"] == "hello"
