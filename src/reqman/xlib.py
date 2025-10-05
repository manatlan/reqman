#!/usr/bin/python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2021 manatlan manatlan[at]gmail(dot)com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# https://github.com/manatlan/reqman
# #############################################################################

from xml.dom import minidom
from xpath import expr
import xpath  # see "pip install py-dom-xpath-six"

from .common import NotFound

class Xml:
    def __init__(self, x:str):
        self.doc = minidom.parseString(x)

    def xpath(self, p:str):
        ll = []
        result = xpath.find(p, self.doc)
        if not isinstance(result, list):
            result = [result]
        for ii in result:
            if isinstance(ii, minidom.Node):
                if ii.nodeType in [minidom.Node.ELEMENT_NODE, minidom.Node.DOCUMENT_NODE]:
                    ll.append(expr.string_value(ii))
                elif ii.nodeType == minidom.Node.TEXT_NODE:
                    assert isinstance(ii, minidom.Text)
                    ll.append(ii.wholeText)
                elif ii.nodeType == minidom.Node.ATTRIBUTE_NODE:
                    assert isinstance(ii, minidom.Attr)
                    ll.append(ii.value)
            else:
                ll.append(str(ii))

        if ll:
            return ll
        else:
            return NotFound

    def __repr__(self):
        xml = self.doc.toprettyxml(indent=" " * 4)
        x = "\n".join(
            [s for s in xml.splitlines() if s.strip()]
        )  # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/
        return x


if __name__=="__main__":
    x=Xml("<a>hello</a>")
    assert x.doc
    l=x.xpath("//a")
    print(l)