import reqman, asyncio,pytest
from pprint import pprint

MOCK={
    "/a": lambda method,url,body,headers: 12/0,
    "/b": (200,"ok"),
}


def test_500(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 500
""")

    x=exe(".","--o",fakeServer=MOCK)
    #x.view()
    assert x.rc == 0

def test_error_in_py_call(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- POST: /b
  body:
    id:   1
    content: <<txt|b64>>
  tests:
    - status: 201
    - json.ok: true
  params:
    txt: hello world
    b64: |
        import base64
        return base64.b64encode( x )

""")

    x=exe(".","--o",fakeServer=MOCK)
    assert x.rc == 2

