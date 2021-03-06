#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
import logging

try:
    from newcore.common import decodeBytes,jdumps
except ModuleNotFoundError:
    from common import decodeBytes,jdumps


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
    if type(x) is bytes:
        return str(x)
    elif type(x) is str:
        return x
    else:
        return jdumps(x)

class Test(int):
    """ a boolean with a name """

    name = ""

    def __init__(self, v, n1, n2, realValue):
        pass  # just for mypy

    def __new__(
        cls, value: int, nameOK: str = None, nameKO: str = None, realValue=None
    ):
        s = super().__new__(cls, value)
        if value:
            s.name = nameOK
        else:
            s.name = nameKO
        s.value = realValue
        return s

    def __repr__(self):
        return "%s: %s" % ("OK" if self else "KO", self.name)


def guessValue(txt):
    """ return a value that is comparable (everything but not bytes)"""
    if type(txt) == bytes:
        return decodeBytes(txt) # to string

    if type(txt) == str:
        if txt=="":
            return None
        else:
            try:
                obj=eval(txt)
                if type(obj)==bytes:
                    return decodeBytes(obj)
                elif obj is None or type(obj) in [bool,int,float,str]:
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
    if type(v) == str:
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
    if type(opeval)==list:
        values=opeval # or [guessValue(i) for i in opeval], but baddest
        val=guessValue(val)
        if type(val)==list: # compare 2 list
            test= val == values
            tok="="
            tko="!="
        else:
            test=val in values
            tok="in"
            tko="not in"
        value=values
    elif type(opeval)==dict:
        val=guessValue(val)
        test = (val == opeval)
        tok="="
        tko="!="
        value=opeval
    else: # or str
        value,fct,tok,tko=getValOpe(opeval)
        value=guessValue(value)

        try:
            val=guessValue(val)
            test=fct(value,val)
        except Exception as e:
            logging.debug(f"testCompare('{var}','{val}','{opeval}') : {e} -> assuming test is negative !")
            test=False

    nameOK = var + " " + tok + " " + strjs(value)  # test name OK
    nameKO = var + " " + tko + " " + strjs(value)  # test name KO
    return Test( test ,nameOK, nameKO,val )

if __name__=="__main__":
    assert( guessValue("41")==41 )
    assert( guessValue(b"[1234]")=="[1234]")
    assert( guessValue("float")=="float")
    assert( guessValue("None")==None)
    assert( guessValue("null")==None)
    assert( guessValue("True")==True)
    assert( guessValue("true")==True)
    
    print( strjs(3.14) )