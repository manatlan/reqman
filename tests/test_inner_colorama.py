#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import reqman

def test_1():
    assert reqman.cr(None) is None
    assert "HELLO" in reqman.cy("HELLO")
    assert "HELLO" in reqman.cr("HELLO")
    assert "HELLO" in reqman.cg("HELLO")
    assert "HELLO" in reqman.cb("HELLO")
    assert "HELLO" in reqman.cw("HELLO")