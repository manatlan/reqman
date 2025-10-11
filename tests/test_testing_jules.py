# -*- coding: utf-8 -*-

import pytest
import json
from reqman.testing import (
    HeadersMixedCase,
    strjs,
    Test,
    guessValue,
    getValOpe,
    testCompare,
    PythonTest,
    CompareTest,
    _convert
)
from reqman.env import Scope
testCompare.__test__ = False

def test_headers_mixed_case_jules():
    h = HeadersMixedCase(ContentType="application/json", X_Custom="value")
    # Test case-insensitive access
    assert h["contenttype"] == "application/json"
    assert h["ContentType"] == "application/json"
    assert h.get("x_custom") == "value"
    assert h.get("X_Custom") == "value"
    # Test non-existent key
    assert h.get("not-exists") is None
    assert h.get("not-exists", "default") == "default"
    # Test __contains__ (which is case-sensitive as it's from dict)
    assert "ContentType" in h
    assert "contenttype" not in h

def test_strjs_jules():
    assert strjs(b"hello") == "b'hello'"
    assert strjs("hello") == "hello"
    assert strjs(123) == "123"
    assert strjs(3.14) == "3.14"
    assert strjs(True) == "true"
    assert strjs(None) == "null"
    assert strjs({"a": 1}) == '{"a": 1}'
    assert strjs([1, 2]) == '[1, 2]'

def test_test_class_jules():
    t_ok = Test(1, "OK", "KO", "value")
    assert bool(t_ok) is True
    assert t_ok.name == "OK"
    assert t_ok.value == "value"
    assert repr(t_ok) == "OK: OK"

    t_ko = Test(0, "OK", "KO", "value")
    assert bool(t_ko) is False
    assert t_ko.name == "KO"
    assert t_ko.value == "value"
    assert repr(t_ko) == "KO: KO"

    t_ko2 = t_ok.toFalse()
    assert bool(t_ko2) is False
    assert t_ko2.name == "KO"
    assert t_ko2.value == "value"
    assert t_ko2._nameOK == "OK"
    assert t_ko2._nameKO == "KO"

def test_guess_value_jules():
    assert guessValue(b"some bytes") == "some bytes"
    assert guessValue("") is None
    assert guessValue("123") == 123
    assert guessValue("3.14") == 3.14
    assert guessValue("True") is True
    assert guessValue("False") is False
    assert guessValue("None") is None
    assert guessValue('{"a": 1}') == {"a": 1}
    assert guessValue('[1, "a"]') == [1, "a"]
    assert guessValue("('a',)") == "('a',)" # eval returns a tuple, which raises Exception
    assert guessValue('string with "quotes"') == 'string with "quotes"'
    assert guessValue("just a string") == "just a string"
    assert guessValue(123) == 123
    assert guessValue(b'{"a":1}') == '{"a":1}'
    assert guessValue("b'hello'") == "hello"
    assert guessValue("b'\\xc3\\xa9'") == "é"
    assert guessValue(None) is None
    assert guessValue({"a":1}) == {"a":1}


def test_get_val_ope_jules():
    # No operator
    v, f, tok, tko = getValOpe("value")
    assert v == "value"
    assert f("value", "value") is True
    assert f("value", "other") is False
    assert tok == "="
    assert tko == "!="

    # All operators
    operators = {
        "==": (lambda a,b: b == a, "=", "!="),
        "=": (lambda a,b: b == a, "=", "!="),
        "!=": (lambda a,b: b != a, "!=", "="),
        ">": (lambda a,b: b is not None and a is not None and b > a, ">", "<="),
        "<": (lambda a,b: b is not None and a is not None and b < a, "<", ">="),
        ">=": (lambda a,b: b is not None and a is not None and b >= a, ">=", "<"),
        "<=": (lambda a,b: b is not None and a is not None and b <= a, "<=", ">"),
        "?": (lambda a,b: str(a) in str(b), "contains", "doesn't contain"),
        "!?": (lambda a,b: str(a) not in str(b), "doesn't contain", "contains"),
    }
    for op, (ref_f, ref_tok, ref_tko) in operators.items():
        v, f, tok, tko = getValOpe(f".{op} 5")
        assert v == "5"
        assert tok == ref_tok
        assert tko == ref_tko

def test_compare_various_types_jules():
    # list vs list
    assert testCompare("var", "[1,2]", [1, 2])
    # item in list
    assert testCompare("var", "1", [1, 2])
    # item not in list
    assert not testCompare("var", "3", [1, 2])
    # content contains one of
    assert testCompare("content", "hello world", ["world", "nope"])
    # dict vs dict
    assert testCompare("var", '{"a":1}', {"a": 1})
    assert not testCompare("var", '{"a":1}', {"a": 2})
    # content string
    assert testCompare("content", "this is the content", "content")
    # content with operator
    assert testCompare("content", "this is the content", ".? is the")

def test_compare_exception_jules():
    # This should be handled gracefully and result in a failed test
    t = testCompare("var", "a", ".> 5")
    assert not t
    assert "var <= 5" in t.name

def test_compare_list_equality_jules():
    t = testCompare("var", "[1,2]", [1,2])
    assert t
    assert t.name == "var = [1, 2]"


def test_PythonTest():
    R=dict(status=201,json=dict(liste=[dict(val=1),dict(val=2)]))
    context=Scope({"R": R, "x": 5})
    t=PythonTest("R.status == 201 and x < 10").test_with_scope( context )
    assert t
    assert "R.status == 201 and x < 10" in t._nameOK
    assert "R.status == 201 and x < 10" in t._nameKO
    assert "not" in t._nameKO
    assert "R.status = 201" in t.value
    assert "x = 5" in t.value
    t=PythonTest("R.json.liste[0].val == 1").test_with_scope( context )
    assert t
    assert "R.json.liste[0].val = 1" in t.value


def test_CompareTest():
    R=dict(status=201)
    context=Scope({"R": R, "x": 5})

    t=CompareTest(var="x",expected="5").test_with_scope( context )
    assert t
    assert t.value==5
    assert t._nameOK == "x = 5"
    assert t._nameKO == "x != 5"

    t=CompareTest(var="R.status",expected="201").test_with_scope( context )
    assert t
    assert t.value==201 # t.value is the value of real 'var'
    assert t._nameOK == "R.status = 201"
    assert t._nameKO == "R.status != 201"

if __name__=="__main__":
    test_PythonTest()
    # test_CompareTest()
