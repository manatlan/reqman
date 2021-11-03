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

import yaml,json,asyncio

if __name__ == "__main__":
    import sys,os
    sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from reqman.env import Scope
import reqman.common

KNOWNVERBS = [
    "GET",
    "POST",
    "DELETE",
    "PUT",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "PATCH",
    "CONNECT",
]

#############################################################################

class RMDslCompileException(Exception): pass
class RMDslRuntimeException(Exception): pass

class OP:
    HTTPVERB="HTTPVERB"
    DECLPROC="DECLPROC"
    CALLPROC="CALLPROC"
    WAIT="WAIT"
    IF="IF"

def same(foreach,params, doc,tests,headers):
    if params==None: params=[None]
    assert type(params) in [dict,list]
    if type(params)==dict: params=[params]

    if doc is None:
        doc=[]
    else:
        assert type(doc)==str,"doc should be string"
        doc=[doc]

    # common to http and call
    tests = toListTuple(tests)
    headers = toListTuple(headers)
    if foreach == None:
        foreach=[]
    else:
        if type(foreach)==list:
            print("*DEPRECATED* avoid foreach for list, prefer params")
            assert len(params)==1, "can't mix foreach list with params list"
            # transform to params
            if params==[None]:
                params=foreach
            else:
                p=params[0]
                params=[ {**i,**p} for i in foreach]
            foreach=[]

        elif type(foreach)==str:
            assert is_dynamic(foreach), "foreach must be dynamic"
            foreach=[foreach]
        else:
            raise Exception(f"bad type foreach={foreach}")

    return foreach,params,doc,tests,headers

def op_HttpVerb(method,path,query=None,body=None,save=None, foreach=None,params=None,doc=None,tests=None,headers=None):
    assert type(path)==str,"path should be string"
    # specific http verbs
    querys = toListTuple(query)
    if type(save) == str:
        saves=[ ("save","<<content>>") ]    # compat reqman v1
    else:
        saves = toListTuple(save)

    foreach, params, doc, tests, headers= same(foreach,params,doc,tests,headers)

    return (OP.HTTPVERB,dict(method=method,path=path,headers=headers,body=body,params=params,tests=tests,doc=doc,saves=saves,querys=querys,foreach=foreach))

def op_Call(name, foreach=None,params=None, doc=None,tests=None,headers=None):
    foreach, params, doc, tests, headers= same(foreach,params, doc,tests,headers)
    return (OP.CALLPROC,dict(name=name,params=params,doc=doc,tests=tests,headers=headers,foreach=foreach))

def op_Wait(time):
    assert type(time) in [str,int,float], f"bad type for time={time}"
    if type(time)==str:
        if is_dynamic(time):
            pass
        else:
            try:
                float(time)
            except:
                raise RMDslCompileException(f"bad type for time={time}, should be a var")

    return (OP.WAIT,dict(time=time))

def op_Decl( name, code ) :
    return (OP.DECLPROC,dict(name=name,code=code))

def op_If( condition, then, elze=None) :
    assert type(condition) in [str,int,bool] or condition is None, "if condition must be a str, int or bool"
    return (OP.IF,{"condition":condition,"then":then,"else":elze})


def is_dynamic(word):
    #TODO: can do a lot better here
    return ("<<" in word) or ("{{" in word)


def toListTuple(d):
    if not d:
        return []
    elif type(d)==dict:
        return list(d.items())
    else:
        return [ (list(i.keys())[0],list(i.values())[0]) for i in d]


def compile(defs) -> list:
    try:

        if type(defs)==dict:
            if defs:
                defs=[defs]
            else:
                defs=[]

        assert type(defs)==list, "Compile only types list or dict"

        ll=[]
        for statement in defs:
            if statement=="break": break

            assert type(statement)==dict

            first,second= list(statement.items())[0]    # The first statement define the OP
            del statement[first]                        # (remove it !!!)
            if first in KNOWNVERBS:
                statement["method"]=first
                statement["path"]=second
                ll.append( op_HttpVerb(**statement) )
            elif first=="call":
                assert type(second) in [list,str], f"Bad call, param should be a list or str"
                if type(second) == str:
                    assert not is_dynamic(second), "can't use a dynamic var in call"
                    second=[second]
                for pname in second:
                    assert type(pname) == str, "use only str name"
                    assert not is_dynamic(pname), "can't use a dynamic var in call"
                    statement["name"]=pname
                    ll.append( op_Call( **statement ) )
            elif first=="wait":
                statement["time"]=second
                ll.append( op_Wait( **statement ) )
            elif first=="if":
                if "then" not in statement: #make it compatible with previous reqmans
                    print("*DEPRECATED* don't use old if statement")
                    statement={"condition":second,"then":compile(statement)}
                else:
                    statement={"condition":second,"then":compile(statement["then"])}
                if "else" in statement:
                    statement["elze"]=compile(statement["else"])
                    del statement["else"]
                ll.append( op_If( **statement ) )
            else: # declare a proc
                statement={"name":first,"code":compile(second)}
                ll.append( op_Decl( **statement ) )
    except Exception as e:
        raise RMDslCompileException(e)

    return ll
#############################################################################


def req(scope:dict, method:str,path:str,headers:dict,body:str,tests:list):
    return f"HTTP {method} {path} {headers} avec {scope}"

def prepare(scope:Scope, **defs):
    """ Ensure compatibility with historic env.call(**) (reqman3) """

    # get global timeout
    try:
        timeout = scope.get("timeout", None)  # global timeout
        timeout = timeout and float(timeout) / 1000.0 or None
    except ValueError:
        timeout = None
    defs["timeout"]=timeout

    # get global proxy
    try:
        proxy = scope.get("proxy", None)  # global proxy (proxy can be None, a str or a dict (see httpx/proxy))
    except :
        proxy = None
    defs["proxies"]=proxy       # named proxies !

    body=defs["body"]
    # ensure content is str
    if body is None:
        body=""
    elif type(body) in [list,dict]: # TEST 972_500 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        body=json.dumps(body)
    elif type(body) == bytes:
        body=reqman.common.decodeBytes(body)
    else:
        body=str(body)
    defs["body"]=body

    defs["doc"] ="\n".join( defs["doc"] )
    defs["headers"] = dict(defs["headers"])
    defs["querys"] = dict(defs["querys"])

    return defs



async def execute(statements:list, scope:Scope = None, incontext:dict = {}, http=None):
    if scope is None: scope=Scope({})
    ll=[]
    declarations={}
    for op,defs in statements:
        if op==OP.HTTPVERB:
            params=defs["params"]

            #get the context (ex: infos from calling)
            # by remaking a defs dict -> ndefs
            ndefs= {**defs,
                "doc": defs["doc"]+incontext.get("doc",[]),
                "tests": defs["tests"]+incontext.get("tests",[]),
                "headers": defs["headers"]+incontext.get("headers",[]),
            }
            del ndefs["params"]
            del ndefs["foreach"]    #TODO

            for p in params:
                s=Scope(scope)
                if p: s.update(p)
                ex= await scope.call(**prepare(s,**ndefs),http=http)

                #TODO: should be placed in scope.call() !?
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TODO: begin/end !
                for saveKey, saveWhat in ex.saves.items():
                    # self.parent.env.save(saveKey, saveWhat, self.parent.name in ["BEGIN","END"])
                    scope[saveKey]=saveWhat
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                ll.append( ex )

        elif op==OP.WAIT:
            time = float(scope.resolve_all(defs["time"])) / 1000 # convert to secondes
            await asyncio.sleep( time )

        elif op==OP.IF:
            condition = scope.resolve_all(defs["condition"])
            block = defs["then" if condition else "else"]
            if block:
                for i in await execute(block,scope, incontext):
                    ll.append(i)

        elif op==OP.DECLPROC:
            name,code = defs["name"],defs["code"]
            declarations[ name ] = code

        elif op==OP.CALLPROC:
            name = defs["name"]
            params=defs["params"]

            if name in declarations:
                # prefer local ones
                code = declarations[ name ]
            else:
                assert name in scope, f"Proc {name} is unknown"
                code = compile( scope[name] )

            for p in params:
                s=Scope(scope)
                if p: s.update(p)
                for i in await execute(code,s, incontext={**defs}):
                    ll.append(i)

        else:
            raise Exception(f"execute an unknown op '{op}'")
    return ll
#############################################################################


def FakeExecute(statements:list, scope:Scope = None, http={}):
    """!!!can't call real http !!!! only mock http({}) so 404 if not defined"""
    return asyncio.run( execute(statements,scope,{},http=http))

if __name__=="__main__":
    y="""

- GET: http://path1
  headers:
    x-kiki: fdsqfds
  params:           # aka foreach
    - jo: 42
    - jo: 43
  tests:
    - content: "hello"

- if: jkkjkj
  then:
      POST: http://path2
      body:
        dfsqfdsqfdsq
      params:
        kiki: 12
  else:
    - wait: 10
    - POST: http://path2
      body:
        dfsqfdsqfdsq
      params:
        kiki: 12

- jo:
    - jim:
        - POST: http://path3
          headers:
            x-kiki: Im'jo
          body: "hhh"
    - call: jim
    - wait: 10
    - call: jim
    - wait: 10
    - call: jim

- call: jo
  params:       # aka foreach
    - name: toto1
      value: 42
    - name: toto2
      value: 42

- call: jo

- GET: http://path10
  params:
    jo: 12

- break

- GET: Doesn't exist
"""

    # y=open("REALTESTS/auto_new_features.yml").read()

    y="""
- proc:
    - wait: 500
    - GET: /nimp
      params:
        p: p
      tests:
        - status: 200
- call: proc
  foreach: <<var>>
  tests:
    - status: 200
"""

    y="""
- GET: /nimp
  tests:
    - json.int: 42
  save:
    XXX: <<json.int>>
    """

    MOCK={
        "https://manatlan.com/nimp": (200,json.dumps(dict(int=42))),
    }

    ll=compile(yaml.load(y))
    for i in ll:
        print(i)

    print(".............................")
    s=Scope(dict(
        vars=[ dict(a=1), dict(a=2) ],
        root="https://manatlan.com",
        headers={"x-me":"hello"},
        mymethod="return 42*3",
    ))
    ll=FakeExecute(ll, s, http=MOCK)
    from pprint import pprint
    pprint(ll)
    print(s)
