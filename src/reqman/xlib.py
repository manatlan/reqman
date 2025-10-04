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
import xpath  # see "pip install py-dom-xpath-six"

from .common import NotFound

class Xml:
    def __init__(self, x:str):
        self.doc = minidom.parseString(x)

    def xpath(self, p:str):
        ll = []
        for ii in xpath.find(p, self.doc):
            if ii.nodeType in [self.doc.ELEMENT_NODE, self.doc.DOCUMENT_NODE]:
                ll.append(xpath.expr.string_value(ii))
            elif ii.nodeType == self.doc.TEXT_NODE:
                ll.append(ii.wholeText)
            elif ii.nodeType == self.doc.ATTRIBUTE_NODE:
                ll.append(ii.value)
            else:  # 'CDATA_SECTION_NODE', 'COMMENT_NODE', 'DOCUMENT_FRAGMENT_NODE', 'DOCUMENT_TYPE_NODE', 'ENTITY_NODE', 'ENTITY_REFERENCE_NODE', 'NOTATION_NODE', 'PROCESSING_INSTRUCTION_NODE'
                raise Exception("Not implemented")

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