#!/usr/bin/python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2025 manatlan manatlan[at]gmail(dot)com
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

import re
import json
import logging
import typing as T

logger = logging.getLogger(__name__)

from .common import decodeBytes,jdumps


class HeadersMixedCase(dict):
    def __init__(self, **kargs):
        dict.__init__(self, **kargs)

    def __getitem__(self, key):
        d = {k.lower(): v for k, v in self.items()}
        return d.get(key.lower(), None)

    def get(self, key, default=None):
        d = {k.lower(): v for k, v in self.items()}
        return d.get(key.lower(), default)



def strjs(x) -> str:
    if isinstance(x, bytes):
        return str(x)
    elif isinstance(x, str):
        return x
    else:
        return jdumps(x)

class Test(int):
    """ a boolean with a name """

    name = ""
    value = ""
    _nameOK:T.Optional[str] = ""
    _nameKO:T.Optional[str] = ""

    def __new__(
        cls, value: int, nameOK: T.Optional[str] = None, nameKO: T.Optional[str] = None, realValue:str|dict|None=None
    ):
        s = super().__new__(cls, value)
        s._nameOK=nameOK
        s._nameKO=nameKO
        if value:
            s.name = nameOK or ""
        else:
            s.name = nameKO or ""
        if isinstance(realValue,dict):
            # new PythonTest
            s.value="\n".join([f"{k} = {v}" for k,v in realValue.items()])
        else:
            # old mechanism
            s.value = realValue
        
        return s

    def __repr__(self):
        return "%s: %s" % ("OK" if self else "KO", self.name)

    def toFalse(self):
        return Test(0,self._nameOK,self._nameKO,self.value)


def guessValue(txt):
    """ return a value that is comparable (everything but not bytes)"""
    if isinstance(txt, bytes):
        return decodeBytes(txt) # to string

    if isinstance(txt, str):
        if txt=="":
            return None
        else:
            try:
                obj=eval(txt)
                if isinstance(obj, bytes):
                    return decodeBytes(obj)
                elif obj is None or isinstance(obj, (bool,int,float,str)):
                    return obj
                else:
                    raise Exception("!!!")
            except:
                try:
                    return json.loads(txt)
                except:
                    try:    #TODO: it it used yet ?!
                        return json.loads('"%s"' % txt.replace('"', '\\"'))
                    except:
                        return txt

    return txt


def getValOpe(v):
    if isinstance(v, str):
        if v.startswith("."):
            g = re.match(r"^\. *([\?!=<>]{1,2}) *(.+)$", v)
            if g:
                op, v = g.groups()
                if op in ["==", "="]:  # not needed really, but just for compatibility
                    return v, lambda a, b: b == a, "=", "!="
                elif op == "!=":
                    return v, lambda a, b: b != a, "!=", "="
                elif op == ">=":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b >= a or False,
                        ">=",
                        "<",
                    )
                elif op == "<=":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b <= a or False,
                        "<=",
                        ">",
                    )
                elif op == ">":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b > a or False,
                        ">",
                        "<=",
                    )
                elif op == "<":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b < a or False,
                        "<",
                        ">=",
                    )
                elif op == "?":
                    return (
                        v,
                        lambda a, b: str(a) in str(b),
                        "contains",
                        "doesn't contain",
                    )
                elif op in ["!?",]:
                    return (
                        v,
                        lambda a, b: str(a) not in str(b),
                        "doesn't contain",
                        "contains",
                    )
    return v, lambda a, b: a == b, "=", "!="

def testCompare(var: str, val, opeval) -> Test:
    if isinstance(opeval, list):
        values=opeval # or [guessValue(i) for i in opeval], but baddest
        val=guessValue(val)
        if isinstance(val, list): # compare 2 list
            test= val == values
            tok="="
            tko="!="
        else:
            if var=="content": # "content" test works like the historic way
                test=any([str(v) in str(val) for v in values])
                tok="contains one of"
                tko="doesn't contain one of"
            else:
                test=val in values
                tok="in"
                tko="not in"
        value=values
    elif isinstance(opeval, dict):
        val=guessValue(val)
        test = (val == opeval)
        tok="="
        tko="!="
        value=opeval
    else: # or str
        if var=="content": # "content" test works like the historic way
            value,fct,tok,tko=getValOpe(opeval)
            fct = lambda a, b: str(a) in str(b) #\
            tok="contains"                      # |-  override ^^
            tko="doesn't contain"               #/
        else:
            value,fct,tok,tko=getValOpe(opeval)
        value=guessValue(value)

        try:
            val=guessValue(val)
            test=fct(value,val)
        except Exception as e:
            logger.debug(f"testCompare('{var}','{val}','{opeval}') : {e} -> assuming test is negative !")
            test=False

    nameOK = var + " " + tok + " " + strjs(value)  # test name OK
    nameKO = var + " " + tko + " " + strjs(value)  # test name KO
    return Test( test ,nameOK, nameKO,val )
######################################################################################################
from typing import Any
import ast

class Tracer:
    resolutions={}
class MyDict(dict):
    # These are dict methods that can't be used directly as attributes
    forbidden = {"items", "pop", "copy", "clear"}

    def __init__(self, d,name):
        self._name=name
        super().__init__(d)

    def _trace(self,k,v):
        if self._name is None:
            Tracer.resolutions[f"{k}"]=v
        else:
            Tracer.resolutions[f"{self._name}.{k}"]=v

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'forbidden'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return super().__getattribute__(name)

    def __getitem__(self, key):
        forbidden = object.__getattribute__(self, 'forbidden')

        # handle _<forbidden>_ pattern
        for real in forbidden:
            if key == f"_{real}_":
                return getattr(super(), real)

        # try normal key
        if dict.__contains__(self, key):
            v = dict.__getitem__(self, key)
            self._trace(key, v)
            return v

        # try replacing "_" by "-"
        if "_" in key:
            okey = key.replace("_", "-")
            if dict.__contains__(self, okey):
                v = dict.__getitem__(self, okey)
                self._trace(key, v)
                return v

        raise KeyError(key)

    def __getattr__(self, key):
        try:
            return self[key]  # délégation directe
        except KeyError:
            raise AttributeError(f"'MyDict' object has no attribute '{key}'")

class MyList(list):
    def __init__(self, liste: list,name):
        self._name=name
        super().__init__(liste)
    def __getitem__(self,idx):
        v=super().__getitem__(idx)
        if self._name is None:
            Tracer.resolutions[f"[{idx}]"]=v
        else:
            Tracer.resolutions[f"{self._name}[{idx}]"]=v
        return v

# transforme un objet python (pouvant contenir des dict et des list) en objet avec accès par attribut
def _convert(obj,name) -> Any:
    if isinstance(obj, dict):
        return MyDict({k:_convert(v,name=f"{name}.{k}" if name else k) for k,v in dict(obj).items()}, name=name)
    elif isinstance(obj, list):
        return MyList([_convert(v,name=f"{name}[{idx}]" if name else f"[{idx}]") for idx,v in enumerate(obj)],name)
    else:
        return obj
    
class PythonTest:
    def __init__(self, statement:str):
        self._statement=statement
    def test_with_scope(self, scope) -> Test:
        Tracer.resolutions={}
        r=eval(self._statement, {**scope._locals_,"_trace_":{}}, _convert(scope,name=None))


        # try:
        #     vars_in_expr = {node.id for node in ast.walk(ast.parse(self._statement)) if isinstance(node, ast.Name)}
        #     print(vars_in_expr)
        #     values = {var: scope.get(var, None) for var in vars_in_expr}
        # except Exception:
        #     values = {}

        # keep traces of most resolved vars (those not a list or a dict) ;-(
        # TODO: can do better ?
        values= {k:v for k,v in Tracer.resolutions.items() if not isinstance(v,(list,dict))}

        def negate_expression(expr_str):
            expr = ast.parse(expr_str, mode='eval').body
            neg_expr = ast.UnaryOp(op=ast.Not(), operand=expr)
            return ast.unparse(ast.Expression(body=neg_expr))
        
        negate_statement = negate_expression(self._statement)
        return Test(bool(r), self._statement, negate_statement, values)

class CompareTest:
    def __init__(self,var:str,expected:str):
        self._var=var
        self._expected=expected

    def test_with_scope(self, scope) -> Test:
        resolved_expected=scope.resolve_string_or_not(self._expected)
        resolved_val=scope.get_var_or_empty(self._var)
        return testCompare(self._var,resolved_val,resolved_expected)

if __name__=="__main__":
    ...
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    # assert( guessValue("41")==41 )
    # assert( guessValue(b"[1234]")=="[1234]")
    # assert( guessValue("float")=="float")
    # assert( guessValue("None")==None)
    # assert( guessValue("null")==None)
    # assert( guessValue("True")==True)
    # assert( guessValue("true")==True)

    # print( strjs(3.14) )

    # assert testCompare("jo","42","42")
    # assert testCompare("content","axa","x")

    # t=testCompare("content","axa","x")
    # print(t)
    # print(t.toFalse())

    # t=testCompare("content","axa",["x","z"]) # DO MORE HERE !!!!
    # print( repr(t) )
    # print( repr(t.toFalse()) )
