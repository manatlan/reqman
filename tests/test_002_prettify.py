import pytest, reqman, json
import datetime,pickle


def test_prettify():
    print( reqman.prettify("<root><a>yolo</a></root>") )
    print( reqman.prettify("<root><a>yolo</a>") )
    print( reqman.prettify(json.dumps( {"a":dict(a=1,b=2),"b":list("abc")}) ) )
    print( reqman.prettify( bytes(range(0,255))) )
    print( reqman.prettify( None ) )
