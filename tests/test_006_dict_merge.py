import pytest, reqman, json

def test_la_base():
  upd={
      "ll": [4,5,6],
      "var": "upd",
      "d":{2:2},

      "var2": "new",
  }

  dic={
      "ll": [1,2,3],
      "var": "orig",
      "d":{1:1},

      "var1": "old",

  }


  reqman.dict_merge(dic,upd)

  assert dic["ll"] == [1,2,3,4,5,6]
  assert dic["var"] == "upd"
  assert dic["var1"] == "old"
  assert dic["var2"] == "new"
  assert dic["d"] == {1:1,2:2}