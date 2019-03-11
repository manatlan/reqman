#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import reqman

def test_1():
    assert reqman.prettify(None)== None 
    assert reqman.prettify("yo")== "yo" 
    assert reqman.prettify("42")== "42" 
    assert reqman.prettify("{not good:json}")== "{not good:json}" 
    assert reqman.prettify('{       "albert":   "jo"   }')== '{\n    "albert": "jo"\n}' 
    assert reqman.prettify('<a><b>yo</b></a>')== '<?xml version="1.0" ?>\n<a>\n    <b>yo</b>\n</a>' 
