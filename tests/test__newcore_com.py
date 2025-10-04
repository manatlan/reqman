import pytest,os,ssl
from src import reqman
from unittest.mock import AsyncMock, patch, MagicMock

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


def test_response_classes_jules():
    # Test Response class
    r = reqman.com.Response(200, {}, b"content", "info")
    assert repr(r) == "<Response 200>"

    # Test ResponseError class
    re = reqman.com.ResponseError("error")
    assert repr(re) == "<ResponseError error>"
    assert re.get_json() is None
    assert re.get_xml() is None

    # Test ResponseTimeout class
    rt = reqman.com.ResponseTimeout()
    assert repr(rt) == "<ResponseTimeout Timeout>"

    # Test ResponseUnreachable class
    ru = reqman.com.ResponseUnreachable()
    assert repr(ru) == "<ResponseUnreachable Unreachable>"

    # Test ResponseInvalid class
    ri = reqman.com.ResponseInvalid("url")
    assert repr(ri) == "<ResponseInvalid Invalid url>"


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_call_json_decode_error_jules(mock_async_client):
    # Mock the response
    mock_response = MagicMock()
    mock_response.headers = {'content-type': 'application/json'}
    mock_response.json.side_effect = reqman.com.json.JSONDecodeError("msg", "doc", 0)
    mock_response.content = b'invalid json'
    mock_response.status_code = 200
    mock_response.reason_phrase = "OK"
    mock_response.http_version = "HTTP/1.1"

    # Mock the client
    mock_instance = mock_async_client.return_value.__aenter__.return_value
    mock_instance.request.return_value = mock_response

    # Call the function
    r = await reqman.com.call("GET", "http://test.com")

    # Assertions
    assert r.status == 200
    assert r.content == b'invalid json'


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_call_ssl_error_jules(mock_async_client):
    # Mock the client to raise SSLError
    mock_instance = mock_async_client.return_value.__aenter__.return_value
    mock_instance.request.side_effect = ssl.SSLError()

    # Call the function
    r = await reqman.com.call("GET", "https://test.com")

    # Assertions
    assert isinstance(r, reqman.com.ResponseUnreachable)


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_call_generic_exception_jules(mock_async_client):
    # Mock the client to raise a generic Exception
    mock_instance = mock_async_client.return_value.__aenter__.return_value
    mock_instance.request.side_effect = Exception("generic error")

    # Call the function
    r = await reqman.com.call("GET", "http://test.com")

    # Assertions
    assert isinstance(r, reqman.com.ResponseUnreachable)


def test_simu_call_exceptions_jules():
    # Test "Bad mock response"
    mock_bad = {
        "/bad": (200,)  # len is 1, so it's a bad response
    }
    r = reqman.com.call_simulation(mock_bad, "GET", "/bad")
    assert r.status == 500
    assert b"mock server error: Bad mock response" in r.content

    # Test when callable mock raises exception
    def f(method, url, body, headers):
        raise ValueError("some error")
    mock_callable_exc = {
        "/": f
    }
    r = reqman.com.call_simulation(mock_callable_exc, "GET", "/")
    assert r.status == 500
    assert b"mock server error: some error" in r.content

    # Test encoding fallback path
    # A character that is not in cp1252
    mock_decode = {
        "/decode": (200, "☃")
    }
    r = reqman.com.call_simulation(mock_decode, "GET", "/decode")
    assert r.status == 200
    assert r.content == "☃".encode('utf-8')
