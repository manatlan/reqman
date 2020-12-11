import pytest, reqman, json
import datetime, pickle


def test_Env_pickable():
    e = reqman.Env({"a": 42})
    assert e == {"a": 42}
    assert pickle.loads(pickle.dumps(e)) == e

    e.save("b", 43)
    assert e == {"a": 42, "b": 43}
    assert pickle.loads(pickle.dumps(e)) == {"a": 42, "b": 43}


def test_Env_cant_save_existing():
    e = reqman.Env({"a": 42})
    assert e == {"a": 42}

    # with pytest.raises(reqman.RMException):
    assert e["a"] == 42
    e.save("a", 43)  # will erase old "a"
    assert (
        e["a"] == 43
    )  # important, to get token oauth first (in current major reqman's tests)!


def test_createEnv():
    assert reqman.Env() == {}
    assert reqman.Env({"a": 42}) == {"a": 42}

    assert reqman.Env(None) == {}
    assert reqman.Env("") == {}

    assert reqman.Env("a: 42") == {"a": 42}


def test_createEnvBad():
    assert reqman.Env(list("abc")) == {}
    assert reqman.Env("[1,2,3]") == {}
    # with pytest.raises(reqman.RMFormatException):
    #     reqman.Env( list("abc") )

    # with pytest.raises(reqman.RMFormatException):
    #     reqman.Env( "[1,2,3]" )

    with pytest.raises(reqman.RMFormatException):
        reqman.Env("- yolo\nbad: yaml")


def test_jpath():
    assert reqman.jpath({"v": 42}, "v") == 42
    assert reqman.jpath({"v": 42}, "v2") is reqman.NotFound

    env = reqman.Env(dict(toto=dict(v1=100, v2=None), tata=dict(l=["a", "b", "c"])))
    assert reqman.jpath(env, "titi") is reqman.NotFound
    assert reqman.jpath(env, "titi.size") is reqman.NotFound
    assert reqman.jpath(env, "titi.0") is reqman.NotFound

    assert reqman.jpath(env, "toto.v1") == 100
    assert reqman.jpath(env, "toto.v2") == None
    assert reqman.jpath(env, "toto.v3") is reqman.NotFound
    assert reqman.jpath(env, "toto.size") == 2

    assert reqman.jpath(env, "tata.l") == ["a", "b", "c"]
    assert reqman.jpath(env, "tata.l.1") == "b"
    assert reqman.jpath(env, "tata.l.1.size") == 1
    assert reqman.jpath(env, "tata.l.size") == 3


def test_jpath_python():
    env = dict(fct="return dict(a=dict(b=42))")
    assert reqman.jpath(env, "fct.size") == 1
    assert reqman.jpath(env, "fct.a.b") == 42


def test_simple():
    dt = datetime.datetime.now()

    env = reqman.Env(
        dict(
            s="world",
            i=42,
            f=3.14,
            t=(1, "kkk"),
            l=[1, "kkk"],
            d=dict(i=42),
            n=None,
            bt=True,
            bf=False,
            dt=dt,
            json={"b": "42", "content-type": "xxx"},
        )
    )
    assert env.replaceTxt("hello '<<>>'") == "hello '<<>>'"
    assert env.replaceTxt("hello '<<unknown>>'") == "hello '<<unknown>>'"
    assert env.replaceTxt("hello '<<s>>'") == "hello 'world'"
    assert env.replaceTxt("hello '<<i>>'") == "hello '42'"
    assert env.replaceTxt("hello '<<f>>'") == "hello '3.14'"
    assert env.replaceTxt("hello '<<t>>'") == """hello '[1, "kkk"]'"""
    assert env.replaceTxt("hello '<<l>>'") == """hello '[1, "kkk"]'"""
    assert env.replaceTxt("hello '<<d>>'") == """hello '{"i": 42}'"""
    assert env.replaceTxt("hello '<<n>>'") == """hello 'null'"""
    assert env.replaceTxt("hello '<<bt>>'") == """hello 'true'"""
    assert env.replaceTxt("hello '<<bf>>'") == """hello 'false'"""
    assert env.replaceTxt("hello '<<dt>>'") == """hello '%s'""" % str(dt)
    assert env.replaceTxt("hello '<<json.b>>'") == """hello '42'"""
    assert env.replaceTxt("hello '<<json.content-type>>'") == """hello 'xxx'"""


def test_complex():
    env = reqman.Env(dict(d=dict(v1=False, v2=None)))
    assert env.replaceTxt("hello '<<d.v1>>'") == "hello 'false'"
    assert env.replaceTxt("hello '<<d.v2>>'") == "hello 'null'"
    assert env.replaceTxt("hello '<<d.v3>>'") == "hello '<<d.v3>>'"


def test_rec():
    env = reqman.Env(dict(v="<<v1>>", v1="<<v2>>", v2="<<value>>", value="ok"))
    assert env.replaceTxt("hello '<<v>>'") == "hello 'ok'"


def test_rec2():
    env = reqman.Env(dict(d={"a": "<<c>>"}, c=42))
    assert env.replaceTxt("hello '<<d>>'") == """hello '{"a": 42}'"""


def test_transform_dynamix():
    env = reqman.Env(dict(v=42, m="return x*'*'"))
    assert (
        env.replaceTxt("hello '<<v|m>>'")
        == "hello '******************************************'"
    )


def test_transform_statix():
    env = reqman.Env(dict(m="return x*'*'"))
    with pytest.raises(reqman.RMPyException):
        env.replaceTxt("hello '<<42|m>>'")
    # assert env.replaceTxt("hello '<<42|m>>'") == "hello '******************************************'"


def test_transform_no_args_return_float():
    env = reqman.Env(dict(pi="return 3.14"))
    assert env.replaceTxt("hello '<<|pi>>'") == "hello '3.14'"


def test_transform_return_int():
    env = reqman.Env(dict(m="return int(x*7)"))
    with pytest.raises(reqman.RMPyException):
        env.replaceTxt("hello '<<42|m>>'")
        # assert env.replaceTxt("hello '<<42|m>>'") == "hello '294'"


def test_transform_return_bytes_and_replace_all():
    env = reqman.Env(dict(m="return b'bijour'"))
    assert env.replaceTxt("hello '<<|m>>'") == b"bijour"


def test_transform_unknown_method():
    env = reqman.Env()
    with pytest.raises(reqman.RMPyException):
        env.replaceTxt("hello '<<v|unknwon>>'")


def test_transform_bad_exception_in_method():
    env = reqman.Env(dict(m="return x/0"))
    with pytest.raises(reqman.RMPyException):
        env.replaceTxt("hello '<<42|m>>'")


def test_replaceObj():
    env = reqman.Env(dict(v=42, b=b"bytes", s="hello"))
    assert env.replaceObj(None) == None
    assert env.replaceObj("yo") == "yo"
    assert env.replaceObj(3.14) == 3.14
    assert env.replaceObj(42) == 42
    assert env.replaceObj(True) == True
    assert env.replaceObj(False) == False
    assert env.replaceObj({"a": "42"}) == {"a": "42"}
    assert env.replaceObj([{"a": "42"}]) == [{"a": "42"}]

    assert env.replaceObj("<<unknown>>") == "<<unknown>>"
    assert env.replaceObj("<<v>>") == 42
    assert env.replaceObj({"a": "<<v>>"}) == {"a": 42}

    assert env.replaceObj("<<b>>") == b"bytes"


def test_replaceObj2():
    env = reqman.Env(dict(obj1=dict(a=42, b="<<obj2>>"), obj2=dict(i=42, j="hello")))
    o = env.replaceObj("<<obj1>>")
    assert o == {"a": 42, "b": {"i": 42, "j": "hello"}}


def test_replaceObj3():
    env = reqman.Env(dict(obj1=dict(a=42, b="<<obj2>>"), obj2="hello"))
    o = env.replaceObj("<<obj1>>")
    assert o == {"a": 42, "b": "hello"}


def test_switches():
    env = reqman.Env(dict(obj1=dict(root="https://w1")))
    assert list(env.switches) == [("obj1", "https://w1")]


def test_renameKeys():
    dd = dict(KEY="kiki", a=42, b=dict(KEY=12, c=13))
    reqman.renameKeyInDict(dd, "KEY", "MyKey")
    assert dd == {"a": 42, "b": {"c": 13, "MyKey": 12}, "MyKey": "kiki"}


def test_HeadersMixed():
    dd = reqman.HeadersMixedCase(KeY="kiki")
    assert dd["KeY"] == "kiki"
    assert dd["key"] == "kiki"
    assert dd["key2"] == None
    assert dd.get("key") == "kiki"
    assert dd.get("key2") == None


## cf "test_300.new.py"
## cf "test_300.new.py"
## cf "test_300.new.py"
## cf "test_300.new.py"
def test_ultracomplex():
    env = reqman.Env(dict(user=dict(id=42, name="kiki"), user1="<<user>>"))
    assert env.replaceTxt("hello '<<user1.id>>'") == "hello '42'"


def test_ultracomplex2():
    env = reqman.Env(dict(user=dict(id=42, name="kiki"), user_id="<<user.id>>"))
    assert env.replaceTxt("hello '<<user_id>>'") == "hello '42'"

def test_ultracomplex3():
    env = reqman.Env(dict(user=dict(info=dict(id=42), name="kiki"), user1="<<user>>"))
    assert env.replaceTxt("hello '<<user1.info.id>>'") == "hello '42'"

def test_ultracomplex4():
    env = reqman.Env(dict(user=dict(info=dict(id=42), name="kiki"), info1="<<user.info>>"))
    assert env.replaceTxt("hello '<<info1.id>>'") == "hello '42'"
