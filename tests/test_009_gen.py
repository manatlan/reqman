import pytest, reqman, json
import datetime,pickle

H=[("X-num",1),("X-str","1"),("content-type","yolo"),("X-User","<<head>>")]

def test_simple():
  x=reqman.GenRML("get","https://www.example.com/path?a=1&b=2#yo", headers=dict(H))
  print(x)

def test_more():
  h=[("X-test","1"),("content-type","yolo")]
  x=reqman.GenRML("post","/path?kif={{hi}}&a=1&a=2#anchor",dict(a=[1,2,3]),H)
  x.params=[("mine","<<value>>")]
  x.tests=[("status",200)]
  x.comment="yoyoy\ndsffdsq" # or ["hhhlo","kkkk"]
  x.returns=dict(a=21)

  x.doc="test\ntest\ntest"
  x.setGenerateParams(True)
  x.setGenerateQuery(True)
  print(x)

#TODO: more more more tests here !!