from context import reqman
import os

def test_1():
    t="héllo".encode().decode("cp1252")
    assert reqman.chardet(t)=="cp1252"

    t="héllo"
    assert reqman.chardet(t)=="utf8"    

    t="hello"
    assert reqman.chardet(t)=="utf8"        