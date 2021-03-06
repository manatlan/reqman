import pytest,json
import newcore.testing


def test_comp():
    compare=lambda x,opeval: newcore.testing.testCompare("my",x,opeval)

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
    compare=lambda x,opeval: newcore.testing.testCompare("my",x,opeval)

    assert compare(200,[200,201])

def test_comp_complex():
    compare=lambda x,opeval: newcore.testing.testCompare("my",x,opeval)

    assert compare(3.14,3.14)

    x=dict(items=list("abc"),value="hello")
    assert compare(x,json.dumps(x))
    assert compare(json.dumps(x),json.dumps(x))

def test_gv():
    o=dict(items=list("abc"),value="hello")

    assert newcore.testing.guessValue("12")==12
    assert newcore.testing.guessValue("3.1")==3.1
    assert newcore.testing.guessValue("hi")=="hi"
    assert newcore.testing.guessValue("true")==True
    assert newcore.testing.guessValue("false")==False
    assert newcore.testing.guessValue("True")==True
    assert newcore.testing.guessValue("False")==False
    assert newcore.testing.guessValue("null")==None
    assert newcore.testing.guessValue("None")==None
    assert newcore.testing.guessValue("[1,2]")==[1,2]

    assert newcore.testing.guessValue(json.dumps(o))==o

    assert newcore.testing.guessValue(b"[1234]")=="[1234]"
    assert newcore.testing.guessValue("b'[1234]'")=="[1234]"  #special base (conv byte'string to string)

    assert newcore.testing.guessValue("float")=="float"

    # assert newcore.utils.guessValue("{'items': ['a', 'b', 'c'], 'value': 'hello'}")==o