import pytest,json
import newcore.utils


def test_comp():
    compare=lambda x,opeval: newcore.utils.testCompare("my",x,opeval)

    assert compare(201,"201")
    assert compare(201,".= 201")
    assert compare(201,".== 201")
    assert compare(201,".> 200")
    assert compare("201",".> 200")
    assert compare("200",".>= 200")
    assert compare("200",".<= 200")
    assert compare("200",".< 201")
    assert compare("200",".!= 201")
    assert compare("200",".!== 201")

    assert compare("ABC",".? A")
    assert compare("ABC",".!? Z")

def test_comp_list():
    compare=lambda x,opeval: newcore.utils.testCompare("my",x,opeval)

    assert compare(200,[200,201])

def test_comp_complex():
    compare=lambda x,opeval: newcore.utils.testCompare("my",x,opeval)

    assert compare(3.14,3.14)

    x=dict(items=list("abc"),value="hello")
    assert compare(x,json.dumps(x))
    assert compare(json.dumps(x),json.dumps(x))

def test_gv():
    o=dict(items=list("abc"),value="hello")

    assert newcore.utils.guessValue("12")==12
    assert newcore.utils.guessValue("3.1")==3.1
    assert newcore.utils.guessValue("hi")=="hi"
    assert newcore.utils.guessValue("true")==True
    assert newcore.utils.guessValue("false")==False
    assert newcore.utils.guessValue("True")==True
    assert newcore.utils.guessValue("False")==False
    assert newcore.utils.guessValue("null")==None
    assert newcore.utils.guessValue("None")=="None"
    assert newcore.utils.guessValue("[1,2]")==[1,2]

    assert newcore.utils.guessValue(json.dumps(o))==o
    # assert newcore.utils.guessValue("{'items': ['a', 'b', 'c'], 'value': 'hello'}")==o