import pytest
from src import reqman
import json,os

ENV=reqman.env.Scope(dict(
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

NotFound = reqman.env.NotFound

def test_b_a_ba():
    assert ENV.get_var("kiki")==3.4
    assert ENV.get_var("a.b")==42
    assert ENV.get_var("a.bb")=="BB"
    assert ENV.get_var("a.bb.size")==2
    assert ENV.get_var("a.bb.0")=="B"
    assert ENV.get_var("a.bb.1")=="B"
    assert ENV.get_var("a.bb.-1")=="B"

    assert ENV.get_var("a.bb.99")==NotFound
    assert ENV.get_var("a.bb.-99")==NotFound

    assert ENV.get_var("a.bb.sizxw")==NotFound
    assert ENV.get_var("a.x")==NotFound
    assert ENV.get_var("XXX")==NotFound

def test_ignorable_vars(): # endings with "?"
    ENV["decor"]=lambda x,ENV: f"-{x}-"
    assert "unknown" not in ENV
    assert ENV.get_var_or_empty("unknown")==""

    assert ENV.get_var("unknown")==NotFound
    assert ENV.get_var("unknown|isEmpty")==NotFound

    assert ENV.get_var("unknown?")==""
    assert ENV.get_var("unknown?|decor")=="--"

    assert ENV.get_var_or_empty("unknown?") == ENV.get_var_or_empty("unknown")  # same behaviour

    with pytest.raises(reqman.env.ResolveException):
        ENV.resolve_string("a txt <<unknown>>")

    assert ENV.resolve_string("a txt <<unknown?>>")==ENV.resolve_string_or_not("a txt <<unknown?>>") # same behaviour

    assert ENV.resolve_string_or_not("a txt <<unknown>>")=="a txt <<unknown>>"

def test_resolve_all1():
    env = reqman.env.Scope(dict(obj1=dict(a=42, b="<<obj2>>"), obj2=dict(i=42, j="hello")))
    o = env.resolve_all("<<obj1>>")
    assert o == {"a": 42, "b": {"i": 42, "j": "hello"}}

def test_resolve_all2():
    env = reqman.env.Scope(dict(v=42))
    assert env.resolve_all({"a": "<<v>>"}) == {"a": 42}


def test_resolve_all():
    ENV["pytest"]=lambda x,ENV: "ttt"
    assert "unknown" not in ENV
    assert ENV.resolve_all("<<kiki>>")==3.4
    assert ENV.resolve_all("<<kiki>><<kiki>>")=="3.43.4"
    assert ENV.resolve_all("   <<kiki>>  ")==3.4
    assert ENV.resolve_all("-<<kiki>>")==-3.4
    assert ENV.resolve_all("nimp <<kiki>>")=="nimp 3.4"

    assert ENV.resolve_all(3.4)==3.4
    assert ENV.resolve_all(None)==None
    assert ENV.resolve_all("kiki")=="kiki"

    with pytest.raises(reqman.env.ResolveException):
        ENV.resolve_all("a txt <<unknown>>")

    assert ENV.resolve_all("<<unknown?>>")==""

    assert ENV.resolve_all("<<pytest>>")=="ttt"
    assert ENV.resolve_all("<<pytest?>>")=="ttt"



def test_get_var_or_empty():
    assert ENV.get_var_or_empty("unknwon|upper") == ""
    assert ENV.get_var_or_empty("byt") == "Hello"
    assert ENV.get_var_or_empty("l") == json.dumps(list("abc"))
    assert ENV.get_var_or_empty("a") == json.dumps(dict(b=42,bb="BB"),)
    assert ENV.get_var_or_empty("a.b") == "42"
    assert ENV.get_var_or_empty("txt2") == "world"

def test_methods():
    assert ENV.get_var("txt|upper") == "HELLO"
    assert ENV.get_var("txt|add1|add2") == "hello12"
    assert ENV.get_var("a.bb|add1") == "BB1"

    assert ENV.get_var("py") == "xxx"
    assert ENV.get_var("py|upper") == "XXX"
    assert ENV.get_var("py|upper|add2") == "XXX2"

    assert ENV.get_var("py2") == dict(a="xxxx")
    assert ENV.get_var("py2.a") == "xxxx"
    assert ENV.get_var("py2.a.0|add2") == "x2"
    assert ENV.get_var("py2.a|upper|add1") == "XXXX1"
    assert ENV.get_var("py2.b") == NotFound

    assert ENV.get_var("txt|unknownMethod") == NotFound

def test_methods_bad():
    with pytest.raises(reqman.env.PyMethodException):
        ENV.get_var("txt|txt2")   #call a non callable
    with pytest.raises(reqman.env.PyMethodException):
        ENV.get_var("upper")      # this method use the param !
    with pytest.raises(reqman.env.PyMethodException):
        ENV.get_var("upper.b")    # non sense
    with pytest.raises(reqman.env.PyMethodException):
        ENV.get_var("upper.0")    # non sense


def test_resolve_stringr():
    x=ENV.resolve_string("fdsgfd <<kiki>> {{a.bb.size}} fdsfds {{py2}}")
    assert x=='fdsgfd 3.4 2 fdsfds {"a": "xxxx"}'

    with pytest.raises(reqman.env.PyMethodException):
        ENV.resolve_string("a txt <<upper>>")    # this method use the param !

    with pytest.raises(reqman.env.ResolveException):
        ENV.resolve_string("a txt <<unknwon>>")  # unknown method

def test_resolve_stringr_or_not():
    assert ENV.resolve_string_or_not("a txt <<upper>>")=="a txt <<upper>>"

    assert ENV.resolve_string_or_not("a txt <<txt2>>")=="a txt world"

    # assert ENV.resolve_string_or_not("a txt <<unknown>>")=="a txt <<unknown>>"

    assert ENV.resolve_string_or_not(b"a txt <<unknown>>")==b"a txt <<unknown>>"
    assert ENV.resolve_string_or_not(42)==42

    assert ENV.resolve_string_or_not("1a <<txt2>> txt <<unknown>>")=="1a world txt <<unknown>>"
    assert ENV.resolve_string_or_not("2a <<unknown>> txt <<txt2>>")=="2a <<unknown>> txt world"


def test_dict():
    e=reqman.env.Scope( dict(response=dict(content="",json=None)) )

    assert e.get_var("response.content") == ""
    assert e.get_var("response.status") == NotFound
    assert e.get_var("response.json") == None
    assert e.get_var("response.json.ll") == NotFound

    with pytest.raises(reqman.env.ResolveException):
        e.resolve_string("<<reponse.status>>")


def test_rec():
    e=reqman.env.Scope( dict(scheme="https",host="://www.manatlan.<<tld>>",tld="com",root="<<scheme>><<host>>") )
    # assert e.resolve_string("<<scheme>><<host>>") =="https://www.manatlan.com"
    assert e.resolve_string("<<root>>") =="https://www.manatlan.com"

    with pytest.raises(reqman.env.ResolveException):
        e=reqman.env.Scope( dict(a="<<b>>",b="<<a>>") )
        e.resolve_string("<<a>>")

def test_order():
    e=reqman.env.Scope( dict(
        a="a",
        b="<<a>>",
        f1=lambda x,Env: x+"1",
        f2=lambda x,Env: x+"2",
    ))
    assert e.resolve_string("<<a|f1>>") == "a1"
    assert e.resolve_string("<<b|f1>>") == "a1"


def test_order2():
    e=reqman.env.Scope( dict(
        upper= lambda x,ENV: x.upper(),
        now = lambda x,ENV: "xxx",
        fichier= "www<<now>>www",
    ))
    assert e.resolve_string("<<fichier|upper>>") == "WWWXXXWWW"

def test_spe():
    e=reqman.env.Scope( dict(
    ))
    with pytest.raises(Exception):
        e.resolve_string(42)

def test_copy_dico():
    e=reqman.env.Scope( dict(
        user=dict(id=42,name="jo"),
        user1="<<user>>",
    ))
    assert isinstance(e.get_var("user"), dict)
    assert e.get_var("user") == dict(id=42,name="jo")
    assert e.get_var("user.id") == 42
    assert e.get_var("user.name") == "jo"

    assert isinstance(e.get_var("user1"), dict)
    assert e.get_var("user1") == dict(id=42,name="jo")
    assert e.get_var("user1.id") == 42
    assert e.get_var("user1.name") == "jo"


def test_dotenv():
    if "ENV_VAR" in os.environ:
        del os.environ["ENV_VAR"]

    e=reqman.env.Scope( dict(
        user="<<ENV_VAR>>",
    ))
    assert e.get_var("ENV_VAR") == NotFound
    assert e.get_var("user") == "<<ENV_VAR>>"


    os.environ["ENV_VAR"]="dotenv_ready"

    assert os.getenv("ENV_VAR") == "dotenv_ready"
    assert os.environ["ENV_VAR"] == "dotenv_ready"

    assert e.get_var("ENV_VAR") == "dotenv_ready"
    assert e.get_var("user") == "dotenv_ready"


@pytest.mark.asyncio
async def test_real_call():
    # e=reqman.env.Env( {} )
    # r=await e.call("GET","/")
    # assert type(r) == reqman.com.ResponseInvalid

    reqman.com.init()

    e=reqman.env.Scope( dict(root="https://www.manatlan.com") )
    r=await e.call("GET","/")
    assert r.status==200,"ko1"

    e=reqman.env.Scope( dict(root="<<scheme>><<host>>",scheme="https",host="://www.manatlan.<<tld>>",tld="com") )
    r=await e.call("GET","/")
    assert r.status==200,f"ko2 {r.content}"


def test_xml():
    e=reqman.env.Scope( dict(
        xml=reqman.xlib.Xml("<a><b>b1</b><b>b2</b><c>c3</c></a>"),
        counter=lambda x,ENV: len(x),

    ))
    assert e.get_var("xml.//b.0") == "b1"
    assert e.get_var_or_empty("xml.//b.0") == "b1"

    assert e.get_var("xml.//b") == ['b1','b2']

    assert e.get_var("xml.//b|//c|//d|//e") == ['b1','b2','c3']
    assert e.get_var("xml.//b|//c|//d|//e|counter") == 3

def test_emptycall():
    e=reqman.env.Scope( dict(
        v="osef",
        now=lambda x,ENV: "xxx",

    ))
    assert e.get_var("v|now") == "xxx"
    assert e.get_var("|now") == "xxx"
    assert e.get_var("vv|now") == NotFound


def test_int_size():
    e=reqman.env.Scope(dict(
        a=dict(cc="12"),
    ))

    assert e.resolve_all("42") == int("42")
    assert e.get_var("a.cc")==int("12")
    assert e.get_var("a.cc.size")==2