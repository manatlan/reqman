import reqman, asyncio,pytest
from pprint import pprint
import json


MOCK={
    "/list": (200,json.dumps( dict(fakeresult=3) )),
    "/3": (200,"ok"),
}


def test_scenario_with_non_resolved(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /list
  tests:
    - status: 200
  save:
    next: <<json.result>>   # "result" doesn't exists

- GET: /<<next>>
  tests:
    status: 200
    content: ok

- GET: /3
  tests:
    status: 200
    content: ok

- GET: /4
  tests:
    status: 404

""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 2 # 2 errors !


