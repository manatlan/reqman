import pytest
import logging
from src import reqman

@pytest.mark.asyncio
async def test_request_logging_jules(caplog):
    """ a new test to check if request are logged """
    env=reqman.env.Scope(dict())
    with caplog.at_level(logging.DEBUG, logger="src.reqman.env"):
        # We use a fake http server to avoid real network calls
        await env.call("GET","http://a.com/path",body="THE BODY",headers={"h1":"v1"}, http={})

    assert "Request: GET http://a.com/path" in caplog.text
    assert "Headers: {'h1': 'v1'}" in caplog.text
    assert "Body: THE BODY" in caplog.text

@pytest.mark.asyncio
async def test_save_variable_logging_jules(caplog):
    """ a new test to check if saved variables are logged """
    # Use a simple scenario that saves the status code
    scenario = """
    - GET: /
      save:
        my_status: <<status>>
    """
    # Use a fake server that returns a 200 OK response
    fake_http = {"/": (200, "ok")}

    reqs = reqman.Reqs(scenario)

    with caplog.at_level(logging.DEBUG, logger="src.reqman"):
        await reqs.asyncReqsExecute([], http=fake_http)

    assert "Saved variable 'my_status' with value: 200" in caplog.text

@pytest.mark.asyncio
async def test_connection_error_logging_jules(caplog):
    """ a new test to check if connection errors are logged """
    # Use a non-routable IP address to trigger a connection error
    # See: https://stackoverflow.com/questions/9045365/what-is-a-non-routable-ip-address
    url = "http://10.255.255.1"

    with caplog.at_level(logging.WARNING, logger="src.reqman.com"):
        await reqman.com.call("GET", url, timeout=0.1)

    assert f"Request to {url} timed out." in caplog.text