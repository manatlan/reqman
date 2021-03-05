import pytest
import newcore.env
import newcore.com
import newcore.xlib
import json

ENV=newcore.env.Env(dict(
    txt="hello",
    txt2="world",
    kiki=3.4,
    a=dict(b=42,bb="BB"),
    byt=b"Hello",
    l=list("abc"),

    py=lambda x,ENV: "xxx",
    py2=lambda x,ENV: {'a':'xxxx'},
    upper= lambda x,ENV: x.upper(),
    add1= lambda x,ENV: x+"1",
    add2= lambda x,ENV: x+"2",
))

NotFound = newcore.env.NotFound

def test_b_a_ba():
    assert ENV.resolve_var("kiki")==3.4
    assert ENV.resolve_var("a.b")==42
    assert ENV.resolve_var("a.bb")=="BB"
    assert ENV.resolve_var("a.bb.size")==2
    assert ENV.resolve_var("a.bb.0")=="B"
    assert ENV.resolve_var("a.bb.1")=="B"
    assert ENV.resolve_var("a.bb.-1")=="B"

    assert ENV.resolve_var("a.bb.99")==NotFound
    assert ENV.resolve_var("a.bb.-99")==NotFound

    assert ENV.resolve_var("a.bb.sizxw")==NotFound
    assert ENV.resolve_var("a.x")==NotFound
    assert ENV.resolve_var("XXX")==NotFound

def test_resolve_var_or_empty():
    assert ENV.resolve_var_or_empty("unknwon|upper") == ""
    assert ENV.resolve_var_or_empty("byt") == "Hello"
    assert ENV.resolve_var_or_empty("l") == json.dumps(list("abc"))
    assert ENV.resolve_var_or_empty("a") == json.dumps(dict(b=42,bb="BB"),)
    assert ENV.resolve_var_or_empty("a.b") == "42"
    assert ENV.resolve_var_or_empty("txt2") == "world"

def test_methods():
    assert ENV.resolve_var("txt|upper") == "HELLO"
    assert ENV.resolve_var("txt|add1|add2") == "hello12"
    assert ENV.resolve_var("a.bb|add1") == "BB1"

    assert ENV.resolve_var("py") == "xxx"
    assert ENV.resolve_var("py|upper") == "XXX"
    assert ENV.resolve_var("py|upper|add2") == "XXX2"

    assert ENV.resolve_var("py2") == dict(a="xxxx")
    assert ENV.resolve_var("py2.a") == "xxxx"
    assert ENV.resolve_var("py2.a.0|add2") == "x2"
    assert ENV.resolve_var("py2.a|upper|add1") == "XXXX1"
    assert ENV.resolve_var("py2.b") == NotFound

    assert ENV.resolve_var("txt|unknownMethod") == NotFound

def test_methods_bad():
    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve_var("txt|txt2")   #call a non callable
    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve_var("upper")      # this method use the param !
    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve_var("upper.b")    # non sense
    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve_var("upper.0")    # non sense


def test_resolver():
    x=ENV.resolve("fdsgfd <<kiki>> {{a.bb.size}} fdsfds {{py2}}")
    assert x=='fdsgfd 3.4 2 fdsfds {"a": "xxxx"}'

    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve("a txt <<upper>>")    # this method use the param !

    with pytest.raises(newcore.env.ResolveException):
        ENV.resolve("a txt <<unknwon>>")  # unknown method

def test_resolver_or_not():
    with pytest.raises(newcore.env.PyMethodException):
        ENV.resolve_or_not("a txt <<upper>>")    # this method use the param !

    assert ENV.resolve_or_not("a txt <<txt2>>")=="a txt world"

    # assert ENV.resolve_or_not("a txt <<unknown>>")=="a txt <<unknown>>"

    assert ENV.resolve_or_not(b"a txt <<unknown>>")==b"a txt <<unknown>>"
    assert ENV.resolve_or_not(42)==42

    assert ENV.resolve_or_not("1a <<txt2>> txt <<unknown>>")=="1a world txt <<unknown>>"
    assert ENV.resolve_or_not("2a <<unknown>> txt <<txt2>>")=="2a <<unknown>> txt world"


def test_dict():
    e=newcore.env.Env( dict(response=dict(content="",json=None)) )

    assert e.resolve_var("response.content") == ""
    assert e.resolve_var("response.status") == NotFound
    assert e.resolve_var("response.json") == None
    assert e.resolve_var("response.json.ll") == NotFound

    with pytest.raises(newcore.env.ResolveException):
        e.resolve("<<reponse.status>>")


def test_rec():
    e=newcore.env.Env( dict(scheme="https",host="://www.manatlan.<<tld>>",tld="com",root="<<scheme>><<host>>") )
    assert e.resolve("<<scheme>><<host>>") =="https://www.manatlan.com"
    assert e.resolve("<<root>>") =="https://www.manatlan.com"

    with pytest.raises(newcore.env.ResolveException):
        e=newcore.env.Env( dict(a="<<b>>",b="<<a>>") )
        e.resolve("<<a>>")

def test_order():
    e=newcore.env.Env( dict(
        a="a",
        b="<<a>>",
        f1=lambda x,Env: x+"1",
        f2=lambda x,Env: x+"2",
    ))
    assert e.resolve("<<a|f1>>") == "a1"
    assert e.resolve("<<b|f1>>") == "a1"


def test_order2():
    e=newcore.env.Env( dict(
        upper= lambda x,ENV: x.upper(),
        now = lambda x,ENV: "xxx",
        fichier= "www<<now>>www",
    ))
    assert e.resolve("<<fichier|upper>>") == "WWWXXXWWW"

def test_copy_dico():
    e=newcore.env.Env( dict(
        user=dict(id=42,name="jo"),
        user1="<<user>>",
    ))
    assert type(e.resolve_var("user"))==dict
    assert e.resolve_var("user") == dict(id=42,name="jo")
    assert e.resolve_var("user.id") == 42
    assert e.resolve_var("user.name") == "jo"

    assert type(e.resolve_var("user1"))==dict
    assert e.resolve_var("user1") == dict(id=42,name="jo")
    assert e.resolve_var("user1.id") == 42
    assert e.resolve_var("user1.name") == "jo"







@pytest.mark.asyncio
async def test_call():
    # e=reqman.env.Env( {} )
    # r=await e.call("GET","/")
    # assert type(r) == reqman.com.ResponseInvalid

    e=newcore.env.Env( dict(root="https://www.manatlan.com") )
    r=await e.call("GET","/")
    assert r.status==200,"ko1"

    e=newcore.env.Env( dict(root="<<scheme>><<host>>",scheme="https",host="://www.manatlan.<<tld>>",tld="com") )
    r=await e.call("GET","/")
    assert r.status==200,f"ko2 {r.content}"


def test_xml():
    e=newcore.env.Env( dict(
        xml=newcore.xlib.Xml("<a><b>b1</b><b>b2</b><c>c3</c></a>"),
        counter=lambda x,ENV: len(x),

    ))
    assert e.resolve_var("xml.//b.0") == "b1"
    assert e.resolve_var_or_empty("xml.//b.0") == "b1"

    assert e.resolve_var("xml.//b") == ['b1','b2']

    assert e.resolve_var("xml.//b|//c|//d|//e") == ['b1','b2','c3']
    assert e.resolve_var("xml.//b|//c|//d|//e|counter") == 3

def test_emptycall():
    e=newcore.env.Env( dict(
        v="osef",
        now=lambda x,ENV: "xxx",

    ))
    assert e.resolve_var("v|now") == "xxx"
    assert e.resolve_var("|now") == "xxx"
    assert e.resolve_var("vv|now") == NotFound
