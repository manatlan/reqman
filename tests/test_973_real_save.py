import reqman, asyncio,pytest
from pprint import pprint
import json
s= dict(int=42,str="hello")

MOCK={
    "/a": (200,json.dumps(s)),
    "/ok/ok/ok/ok": (200,"ok"),
}


def test_savvve(exe):

    with open("reqman.conf","w+") as fid:
        fid.write("""
testByte: |
    return "ok" if type(x)==bytes else "ko"
testInt: |
    return "ok" if type(x)==int else "ko"
testStr: |
    return "ok" if type(x)==str else "ko"
""")

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
    - json.int: 42
    - json.str: hello
  save:
    isOkS: <<status|testInt>>
    isOk: <<content|testByte>>
    isOk2: <<json.int|testInt>>
    isOk3: <<json.str|testStr>>

- GET: /<<isOkS>>/<<isOk>>/<<isOk2>>/<<isOk3>>
  tests:
    status: 200

""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0


