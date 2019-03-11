#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import reqman

def test_1():
    b=reqman.Content("héllo".encode("cp1252"))
    assert repr(b)=="héllo".encode("cp1252").decode("cp1252")
    assert b.toBinary()=="héllo".encode("cp1252")
    assert "llo" in b

def test_2():
    b=reqman.Content("héllo".encode("utf8"))
    assert repr(b)=="héllo".encode("utf8").decode("utf8")
    assert b.toBinary()=="héllo".encode("utf8")
    assert "llo" in b


def test_3():
    bin = bytes( list(range(255,0,-1)) )
    b=reqman.Content(bin)
    assert "BINARY SIZE" in repr(b)
    assert b.toBinary()==bin
