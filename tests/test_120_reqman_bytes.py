import pytest,reqman,json,yaml
import pytest,reqman,json
MOCK={
          "/pingpong": lambda m,p,b,h: (200,b)
      }


def test_newway(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
bytes: |
  return bytes(range(0,255))
"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- POST: /pingpong
  body: Hello World
  tests:
    - status: 200
    - content: .? Hello

- POST: /pingpong
  body:
    a:
        - 1
        - 2
    b: "hello"
  tests:
    - status: 200
    - content: .? hello
    - json.a.0: 1
    - json.a.1: 2
    - json.b: "hello"


- POST: /pingpong
  body: 42
  tests:
    - status: 200
    - content: 42




- POST: /pingpong
  tests:
    - status: 200
    - content: ""

- POST: /pingpong
  body: null
  tests:
    - status: 200
    - content: ""




- POST: /pingpong
  body: <<bytes>>
  tests:
    - status: 200
    - content: .? ABCDEF       # test repr

- POST: /pingpong
  body: <<bytes>>
  tests:
    - status: 200
    - content: <<bytes>>    # test real bytes




- POST: /pingpong
  body: <<|giveBytes>>
  tests:
    - status: 200
    - content: ABCDEF       # test repr
  params:
    giveBytes: return b"ABCDEF"

- POST: /pingpong
  body: <<|giveBytes>>
  tests:
    - status: 200
    - content: <<|giveBytes>>   # test real bytes
  params:
    giveBytes: return b"ABCDEF"


"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0