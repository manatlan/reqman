#!/usr/bin/python
# -*- coding: utf-8 -*-



SERVER={
    "/jo1" : (200, "42"),
    "/jo2" : (200, "42"),
    "/jo3" : (200, "42"),
}


def test_1(client):
    x=client("new","http://jim/jo1")
    assert x.code==0
    assert x.html is None
    assert "Create reqman.conf" in x.console
    assert "Create 0010_test.rml" in x.console

    assert "GET: /jo1" in open("0010_test.rml").read()
    assert "root: http://jim" in open("reqman.conf").read()

    x=client("new","http://jim/jo2")
    assert "Using 'reqman.conf" in x.console
    assert "Create 0020_test.rml" in x.console
    assert "GET: /jo2" in open("0020_test.rml").read()

    x=client("new","/jo3")
    assert "Using 'reqman.conf" in x.console
    assert "Create 0030_test.rml" in x.console
    assert "GET: /jo3" in open("0030_test.rml").read()

    x=client(".")
    assert x.code==0
    assert x.inproc.ok==3

