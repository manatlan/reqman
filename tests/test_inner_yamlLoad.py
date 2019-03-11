#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import reqman
from io import BytesIO
def test_1():
    fd=BytesIO("yo: éé".encode("cp1252"))
    assert reqman.yamlLoad(fd) == dict(yo="éé")
def test_2():
    fd=BytesIO("yo: éé".encode("utf8"))
    assert reqman.yamlLoad(fd) == dict(yo="éé")
