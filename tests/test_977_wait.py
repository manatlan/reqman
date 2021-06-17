import reqman, asyncio,pytest
from pprint import pprint
import json
s= dict(int=500,str="hello")

MOCK={
    "/a": (200,json.dumps(s)),
    "/b": (200,json.dumps(s)),
}


def test_wait_ok(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
  save:
    time: <<json.int>>

- wait: <<time>>

- GET: /b
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0


def test_wait_ko(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
  save:
    time: <<json.int>>

- wait: <<kki>>

- GET: /b
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
""")

    x=exe(".",fakeServer=MOCK)
    assert "WARNING" in x.console
    assert "can't" in x.console
    assert "wait" in x.console
    assert x.rc == 0

