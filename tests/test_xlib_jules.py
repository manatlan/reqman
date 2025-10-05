# -*- coding: utf-8 -*-

from reqman.xlib import Xml
from reqman.common import NotFound

def test_xml_repr_jules():
    x = Xml("<r><a/></r>")
    assert '<?xml version="1.0" ?>' in repr(x)
    assert "<r>" in repr(x)
    assert "<a/>" in repr(x)
    assert "</r>" in repr(x)

def test_xpath_text_node_jules():
    # This test is to ensure coverage of TEXT_NODE handling
    xml_string = "<a>text1<b>text2</b></a>"
    x = Xml(xml_string)
    # This should select the text node 'text1' which is a direct child of 'a'
    result = x.xpath("//a/text()")
    assert result == ["text1"]

def test_xpath_all_text_nodes_jules():
    xml_string = "<a>text1<b>text2</b></a>"
    x = Xml(xml_string)
    # This should select all text nodes in the document
    result = x.xpath("//text()")
    assert sorted(result) == sorted(["text1", "text2"])

def test_xpath_attribute_node_jules():
    # This test is to ensure coverage of ATTRIBUTE_NODE handling
    xml_string = '<a href="http://example.com">link</a>'
    x = Xml(xml_string)
    result = x.xpath("//a/@href")
    assert result == ["http://example.com"]

def test_xpath_not_found_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("//c")
    assert result is NotFound

def test_xpath_element_node_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("//b")
    assert result == ["hello"]

def test_xpath_document_node_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("/")
    assert result == ["hello"]

def test_xpath_non_node_result_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("string-length('hello')")
    assert result == ["5"]

def test_xpath_boolean_result_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("starts-with('hello', 'he')")
    assert result == ['True']

def test_xpath_number_result_jules():
    xml_string = "<a><b>hello</b></a>"
    x = Xml(xml_string)
    result = x.xpath("count(//b)")
    assert result == ['1']