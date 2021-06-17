import pytest, reqman, json,pytest
import datetime,pickle


def test_prettify():
    print( reqman.prettify(b"<root><a>yolo</a></root>") )
    print( reqman.prettify(b"<root><a>yolo</a>") )
    print( reqman.prettify(json.dumps( {"a":dict(a=1,b=2),"b":list("abc")}).encode() ) )
    print( reqman.prettify( bytes(range(0,255))) )
    with pytest.raises( AssertionError ):
         reqman.prettify( None )
    with pytest.raises( AssertionError ):
         reqman.prettify( "hello" )
    with pytest.raises( AssertionError ):
         reqman.prettify( 42 )


def test_guess():
    b=bytes(range(0,255))
    assert reqman.guessValue("jijiij")=="jijiij"
    assert reqman.guessValue('jij"iij')=='jij"iij'
    assert reqman.guessValue('jij"i"ij')=='jij"i"ij'
    assert reqman.guessValue("jij'iij")=="jij'iij"
    assert reqman.guessValue("42")==42
    assert reqman.guessValue("2.5")==2.5
    assert reqman.guessValue("0.2")==.2
    assert reqman.guessValue("0.2.1")=="0.2.1"
    assert reqman.guessValue("null") == None
    assert reqman.guessValue("true") == True
    assert reqman.guessValue("false") == False
    assert reqman.guessValue("{}") == {}
    assert reqman.guessValue("[]") == []

    assert reqman.guessValue(42)==42
    assert reqman.guessValue(b"h")==b"h"
    assert reqman.guessValue(str(b))==str(b)
    assert reqman.guessValue(None)==None