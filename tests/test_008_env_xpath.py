import pytest, reqman, json
import datetime,pickle


xml="""<?xml version="1.0" encoding="UTF-8"?>
<x xmlns:ns2="www">
    <entete>
        <ns2:typeDocument>hello</ns2:typeDocument>
    </entete>
    <a v="1">aaa1</a>
    <a>aaa2</a>
    <b v="9">b9</b>
    <b v="11">b11</b>
    <c>yolo <i>xxx</i></c>
</x>"""

def test_soapresponse():
    xx="""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header>header</SOAP-ENV:Header>
    <SOAP-ENV:Body>
        <result>hello</result>
        <result2 xmlns="myns">hello2</result2>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""
    x=reqman.Xml(xx)
    assert x.xpath("//result")==["hello"]
    assert x.xpath("//result/text()")==["hello"]
    assert x.xpath("//SOAP-ENV:Header")==["header"]
    assert x.xpath("//*:Header")==["header"]
    assert x.xpath("//*[local-name()='result2']")==["hello2"]
    assert x.xpath("//*:result2")==["hello2"]

def test_xpath():
    x=reqman.Xml(xml)
    assert x.xpath("//unknown")==reqman.NotFound
    assert x.xpath("//c")==["yolo xxx"]
    assert x.xpath("//b[@v>10]")==["b11"]
    assert x.xpath("//b[@v<10]")==["b9"]
    assert x.xpath("//b[@v]")==["b9","b11"]
    assert x.xpath("//ns2:typeDocument")==["hello"]
    assert x.xpath("//a")==["aaa1","aaa2"]
    assert x.xpath("//a/text()")==["aaa1","aaa2"]
    assert x.xpath("//a[1]")==["aaa1"]
    assert x.xpath("//a[2]")==["aaa2"]
    assert x.xpath("//a[last()-1]/text()")==["aaa1"]
    assert x.xpath("//a/@v")==["1"]
    assert x.xpath("//b/@v")==['9', '11']
    assert x.xpath("//a|//b")==['aaa1', 'aaa2', 'b9', 'b11']

def test_simple():
    env = reqman.Env(
        dict(
            xml=reqman.Xml(xml),
            s="world",
            upper= "return x.upper()",
        )
    )
    assert env.replaceTxt("hello '<<xml.//a[1].0>>'") == "hello 'aaa1'"
    assert env.replaceTxt("hello '<<s>>'") == "hello 'world'"
    assert env.replaceTxt("hello '<<s|upper>>'") == "hello 'WORLD'"
    assert env.replaceTxt("hello '<<xml.//a[1].0|upper>>'") == "hello 'AAA1'" # can't work with xpath '|' !!!!!!!!!!!!!!
    assert "<entete>" in env.replaceTxt("hello '<<xml>>'")

    print(env["xml"])

