import reqman, asyncio, pytest
from pprint import pprint
import json

MOCK = {
  "/test?hello=42": (200, "ok"),
  "/over": (200, "ok"),
  "/over?hello=41&hello=42": (200, "ok"),
}


def test_simplest(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
VAL: 42
"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /test?hello=42       # classic way
  tests:
    - status: 200

- GET: /test                # new way
  query:
    hello: 42
  tests:
    - status: 200

- GET: /test                # new way
  query:
    hello: <<VAL>>
  tests:
    - status: 200

- GET: /test                # new way
  query:
    hello: <<val>>
  params:
    val: 42
  tests:
    - status: 200

- GET: /test                # new way
  query:
    hello: <<val>>
  params:
    val:
      return 42
  tests:
    - status: 200

- method1:
    GET: /test                # new way
    query:
      hello: <<val>>
    tests:
      - status: 200
- call: method1
  params:
    val: 42



"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0



def test_override(exe):


    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /over?hello=42                # new way
  query:
    hello:                           # override (remove var)
  tests:
    - status: 200

- GET: /over?hello=41                # new way
  query:
    hello: 42                        # override (append value)
  tests:
    - status: 200

- GET: /over
  query:
    hello:
      - 41
      - 42
  tests:
    - status: 200

- GET: /over
  query:
    hello:
      - 41
      - <<var>>
  params:
    var: 42
  tests:
    - status: 200

- GET: /over
  query:
    hello: <<method>>
  params:
    method:
      return [41,42]
  tests:
    - status: 200


- method2:
  - method1:
      GET: /over                # new way
      query:
        hello: 41
      tests:
        - status: 200
  - call: method1
    query:
      hello: 42

- call: method2

"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    assert x.rc == 0



def test_cant1(exe):


    with open("f.yml", "w+") as fid:
        fid.write(
            """

- GET: /over
  query: <<kvs>>
  params:
    kvs:
      hello: [41,42]
  tests:
    - status: 200

"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    assert "query is malformed" in x.console
    assert x.rc == -1

def test_cant2(exe):


    with open("f.yml", "w+") as fid:
        fid.write(
            """

- GET: /over
  query: <<method>>
  params:
    method:
      return dict(hello=[41,42])
  tests:
    - status: 200

"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    assert "query is malformed" in x.console
    assert x.rc == -1
