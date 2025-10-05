# -*- coding: utf-8 -*-

import pytest
import httpx
import ssl
from unittest.mock import patch, MagicMock, AsyncMock

from reqman.com import (
    jdumps,
    init,
    Response,
    ResponseError,
    ResponseTimeout,
    ResponseUnreachable,
    ResponseInvalid,
    call,
    call_simulation,
)

def test_jdumps_jules():
    assert jdumps({"a": "é"}) == '{"a": "é"}'

@pytest.mark.asyncio
async def test_init_jules():
    # just test it runs without error
    i = init()
    async with i:
        pass
    assert True

def test_response_classes_jules():
    r = Response(200, {"Content-Type": "text/plain"}, b"content", "info")
    assert r.status == 200
    assert r.headers == {"Content-Type": "text/plain"}
    assert r.content == b"content"
    assert r.info == "info"
    assert r.error == ""
    assert repr(r) == "<Response 200>"

    re = ResponseError("some error")
    assert re.status is None
    assert re.content == b"some error"
    assert re.error == "some error"
    assert repr(re) == "<ResponseError some error>"
    assert re.get_json() is None
    assert re.get_xml() is None

    rt = ResponseTimeout()
    assert rt.error == "Timeout"
    assert repr(rt) == "<ResponseTimeout Timeout>"

    ru = ResponseUnreachable()
    assert ru.error == "Unreachable"
    assert repr(ru) == "<ResponseUnreachable Unreachable>"

    ri = ResponseInvalid("http://invalid")
    assert ri.error == "Invalid http://invalid"
    assert repr(ri) == "<ResponseInvalid Invalid http://invalid>"

@pytest.mark.asyncio
async def test_call_ssl_error_jules():
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(side_effect=ssl.SSLError)
        response = await call("GET", "https://example.com")
        assert isinstance(response, ResponseUnreachable)

@pytest.mark.asyncio
async def test_call_unhandled_exception_jules():
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(side_effect=ValueError("Some other error"))
        response = await call("GET", "https://example.com")
        assert isinstance(response, ResponseUnreachable)

def test_call_simulation_callable_mock_jules():
    def mock_callable(method, url, body, headers):
        return 201, "Created", {"X-Foo": "Bar"}

    http_mock = {"/": mock_callable}
    r = call_simulation(http_mock, "POST", "/", b"data")
    assert r.status == 201
    assert r.content == b"Created"
    assert r.headers["X-Foo"] == "Bar"

def test_call_simulation_bad_response_jules():
    # Not a tuple/list
    r = call_simulation({"/": "string response"}, "GET", "/")
    assert r.status == 500
    assert b"mock server error" in r.content

    # Tuple with wrong number of elements
    r = call_simulation({"/": (200,)}, "GET", "/")
    assert r.status == 500
    assert b"mock server error" in r.content

def test_call_simulation_callable_exception_jules():
    def mock_callable(method, url, body, headers):
        raise ValueError("mock error")

    http_mock = {"/": mock_callable}
    r = call_simulation(http_mock, "GET", "/")
    assert r.status == 500
    assert b"mock server error: mock error" in r.content

def test_call_simulation_content_encoding_jules():
    # cp1252 encodable string "€" will fallback to utf-8 encoding
    r = call_simulation({"/": (200, "€")}, "GET", "/")
    assert r.content == "€".encode("utf-8")

    # utf-8
    r = call_simulation({"/": (200, "你好")}, "GET", "/")
    assert r.content == "你好".encode("utf-8")

@pytest.mark.asyncio
async def test_call_json_decode_error_jules():
    mock_response = httpx.Response(
        200,
        headers={'content-type': 'application/json'},
        content=b'{"invalid json",}'
    )
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        response = await call("GET", "https://example.com")
        assert response.status == 200
        assert response.content == b'{"invalid json",}'