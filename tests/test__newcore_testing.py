import pytest,json
from src import reqman


def test_comp():
    compare=lambda x,opeval: reqman.testing.testCompare("my",x,opeval)

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
    compare=lambda x,opeval: reqman.testing.testCompare("my",x,opeval)

    assert compare(200,[200,201])

def test_comp_complex():
    compare=lambda x,opeval: reqman.testing.testCompare("my",x,opeval)

    assert compare(3.14,3.14)

    x=dict(items=list("abc"),value="hello")
    assert compare(x,json.dumps(x))
    assert compare(json.dumps(x),json.dumps(x))

def test_gv():
    o=dict(items=list("abc"),value="hello")

    assert reqman.testing.guessValue("12")==12
    assert reqman.testing.guessValue("3.1")==3.1
    assert reqman.testing.guessValue("hi")=="hi"
    assert reqman.testing.guessValue("true")==True
    assert reqman.testing.guessValue("false")==False
    assert reqman.testing.guessValue("True")==True
    assert reqman.testing.guessValue("False")==False
    assert reqman.testing.guessValue("null")==None
    assert reqman.testing.guessValue("None")==None
    assert reqman.testing.guessValue("[1,2]")==[1,2]

    assert reqman.testing.guessValue(json.dumps(o))==o

    assert reqman.testing.guessValue(b"[1234]")=="[1234]"
    assert reqman.testing.guessValue("b'[1234]'")=="[1234]"  #special base (conv byte'string to string)

    assert reqman.testing.guessValue("float")=="float"

    # assert reqman.utils.guessValue("{'items': ['a', 'b', 'c'], 'value': 'hello'}")==o

def test_test():
    assert reqman.testing.testCompare("jo","42","42")

def test_compare_content_normal():
    t=reqman.testing.testCompare("content","axa","x")  # test "content contains"!
    assert t
    assert "contains" in t.name

    t2=t.toFalse()  # test negativity the test
    assert not t2
    assert "doesn't contain" in t2.name
    assert t.value == t2.value

    #---------------------

    obj=dict(albert="x")
    t=reqman.testing.testCompare("content",obj,"x")  # test "content contains"!
    assert t
    assert "contains" in t.name

    t2=t.toFalse()  # test negativity the test
    assert not t2
    assert "doesn't contain" in t2.name
    assert t.value == t2.value


def test_compare_content_with_list():
    t=reqman.testing.testCompare("content","axa",["x","z"])
    assert t
    assert "contains one of" in t.name

    t2=t.toFalse()  # test negativity the test
    assert not t2
    assert "doesn't contain one of" in t2.name
    assert t.value == t2.value

    #---------------------

    obj=dict(albert="x")
    t=reqman.testing.testCompare("content",obj,["x","z"])
    assert t
    assert "contains one of" in t.name

    t2=t.toFalse()  # test negativity the test
    assert not t2
    assert "doesn't contain one of" in t2.name
    assert t.value == t2.value
