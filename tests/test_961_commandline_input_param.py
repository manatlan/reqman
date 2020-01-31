import reqman, asyncio,pytest
from pprint import pprint
import json

MOCK={
    "/ok": (200,"ok"),
}


def test_ko(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<var>>
  tests:
    - status: 404
""")

    x=exe(".","--o",fakeServer=MOCK)
    # x.view()
    assert x.rc == 1 #1 error coz the 404 test is non playable


def test_ok(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<var>>
  tests:
    - status: 200
    - content: ok
""")

    x=exe(".","var:ok","--o",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0




