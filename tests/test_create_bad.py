#!/usr/bin/python
# -*- coding: utf-8 -*-



SERVER={
}


def test_1(client):
    x=client("new","gfdfds")
    assert x.code==-1
    assert "you shoul provide a full url" in x.console