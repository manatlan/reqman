import reqman, asyncio,pytest
from pprint import pprint

MOCK={
    "/a": lambda method,url,body,headers: 12/0,
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

