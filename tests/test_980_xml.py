import reqman, asyncio,pytest
from pprint import pprint
import json
s= dict(int=42,str="hello")

MOCK={
    "/xml": (200,"""<?xml version="1.0" encoding="UTF-8"?>
<x xmlns:ns2="www">
    <entete>
        <ns2:typeDocument>hello</ns2:typeDocument>
    </entete>
    <a v="1">aaa1</a>
    <a>aaa2</a>
    <b v="9">b9</b>
    <b v="11">b11</b>
    <c>yolo <i>xxx</i></c>
</x>"""),
    "/noxml": (200,"""jkjhhjjhhhjhjhjjhjggfgffg"""),
    "/aaa2": (200,"ok")
}


def test_xpath_ok(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /xml
  tests:
    - status: 200
    - json.result: null
    - xml.//c.0 : "yolo xxx"
    - xml.//c.0.size   : 8
    - xml.//a: ["aaa1","aaa2"]
    - xml.//a[1].0: "aaa1"
    - xml.//a[last()].0: "aaa2"
    - xml.//a/text(): ["aaa1","aaa2"]
    - xml.//a.size : .=2
    - xml.//a[@v].0: "aaa1"
    - xml.//a[@v]/@v.0: 1
    - xml.//a|//b: ["aaa1","aaa2","b9","b11"]
    - xml.//a|//b.size: 4
    - xml.//*:nooooo: null
    - xml.//ns2:typeDocument.0: hello
    - xml.//c: .>1                       # bad
    
""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 1  # the bad one ^^



def test_xpath_ko(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /noxml
  tests:
    - status: 200
    - json.result: null
    - xml.//nooooo: null
""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0


def test_xpath_compute(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /xml
  tests:
    - status: 200
  save:
    redirect:  <<xml.//a[last()]>>

- GET: /<<redirect.0>>
  tests:
    - status: 200

""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console) 
    # x.view()
    assert x.rc == 0

def test_xpath_compute2(exe):

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /xml
  tests:
    - status: 200
  save:
    redirect:  <<xml.//a[last()].0>>

- GET: /<<redirect>>
  tests:
    - status: 200

""")

    x=exe(".","--o",fakeServer=MOCK)
    # print(x.console) 
    # x.view()
    assert x.rc == 0

