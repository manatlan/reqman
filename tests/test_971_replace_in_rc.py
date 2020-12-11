import reqman, asyncio, pytest
from pprint import pprint

MOCK = {
    "/a": lambda method, url, body, headers: (200, "ok")
    if headers.get("auth") == "ok"
    else (404, "no"),
    "/yes": (200, "ok"),
}


def test_replace_headers_in_rc(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
user1:
  auth: "ok"
  x-autre2: hello2

headers:
  <<user1>>
"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /a
  headers: 
    auth: null #override
    x-autre: hello
  tests:
    - status: 404
- GET: /a
  headers:
    auth: "ko"
    x-autre: hello
  tests:
    - status: 404
- GET: /a
  headers:
    x-autre: hello
  tests:
    - status: 200
"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    assert x.rc == 0


def test_bad_headers_in_rc(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
user1: 412
  
headers:
  <<user1>>
"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /yes
  tests:
    - status: 200
"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    # x.view()
    assert x.rc == 1  # 1 error


def test_bad_headers2_in_rc(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
 
headers:
  <<user1>>
"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /yes
  tests:
    - status: 200
"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    assert x.rc == 1  # 1 error


def test_replace_headers2_in_rc(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """

token: "no"

headers:
  auth: <<token>>

switchs:
    mod:
        token: "ok"

    headers:
        auth: <<token>>


"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /a
  headers: 
    auth: null #override
    x-autre: hello
  tests:
    - status: 404
- GET: /a
  headers:
    auth: "ko"
    x-autre: hello
  tests:
    - status: 404
- GET: /a
  headers:
    x-autre: hello
  tests:
    - status: 200
"""
        )

    x = exe(".", "-mod", "--o", fakeServer=MOCK)
    # x.view()
    assert x.rc == 0
