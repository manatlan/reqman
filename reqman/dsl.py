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

import yaml

if __name__ == "__main__":
    import sys,os
    sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from reqman.env import Scope

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

    # specific http verbs
    query = toListTuple(query)
    if type(save) == str:
        save={ save: "<<content>>" }    # compat reqman v1
    else:
        save = toListTuple(save)

    foreach, params, doc, tests, headers= same(foreach,params,doc,tests,headers)

    return (OP.HTTPVERB,dict(method=method,path=path,headers=headers,body=body,params=params,tests=tests,doc=doc,save=save,query=query,foreach=foreach))

def op_Call(name, foreach=None,params=None, doc=None,tests=None,headers=None):
    foreach, params, doc, tests, headers= same(foreach,params, doc,tests,headers)
    return (OP.CALLPROC,dict(name=name,params=params,doc=doc,tests=tests,headers=headers,foreach=foreach))

def op_Wait(time):
    assert type(time) in [str,int], f"bad type for time={time}"
    return (OP.WAIT,dict(time=time))

def op_Decl( name, code ) :
    return (OP.DECLPROC,dict(name=name,code=code))

def op_If( condition, then, elze=None) :
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


def compile(defs, declares={}) -> list:
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

            first,second= list(statement.items())[0]
            del statement[first]
            if first in ["GET","POST","PUT","DELETE"]:
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
                    assert pname in declares.keys(), f"calling an unknown proc '{pname}'"
                    statement["name"]=pname
                    ll.append( op_Call( **statement ) )
            elif first=="wait":
                statement["time"]=second
                ll.append( op_Wait( **statement ) )
            elif first=="if":
                if "then" not in statement: #TODO
                    print("*DEPRECATED* don't use old if statement")
                    statement={"condition":second,"then":compile(statement,declares)}
                else:
                    statement["condition"]=second
                    statement["then"]=compile(statement["then"],declares)
                if "else" in statement:
                    statement["elze"]=compile(statement["else"],declares)
                    del statement["else"]
                ll.append( op_If( **statement ) )
            else: # declare a proc
                statement["name"]=first
                statement["code"]=compile(second,declares)
                declares[first] = 1
                ll.append( op_Decl( **statement ) )
    except Exception as e:
        raise RMDslCompileException(e)

    return ll
#############################################################################


def req(scope:dict, method:str,path:str,headers:dict,body:str,tests:list):
    return f"HTTP {method} {path} {headers} avec {scope}"

def pscope(scope:dict,p=None):
    if p is None:
        return {**scope}
    else:
        assert type(p)==dict
        return {**scope,**p}

def execute(statements:list, scope={}):
    declarations={}
    for op,defs in statements:
        if op==OP.HTTPVERB:
            params=defs["params"]

            ndefs={"OP":"HTTP","IF":[True],**defs}          # copy the dict
            del ndefs["params"]     # remove 'params' from copied one

            for p in params:
                ndefs["scope"] = pscope(scope,p)
                yield ndefs

        elif op==OP.WAIT:
            yield {"OP":"WAIT","time":defs["time"],"IF":[True]}

        elif op==OP.IF:
            condition = defs["condition"]
            for i in execute(defs["then"],scope):
                yield {**i,
                    "IF": i["IF"]+[condition],
                }
            for i in execute(defs["else"],scope):
                yield {**i,
                    "IF": i["IF"]+["NOT "+condition],
                }

        elif op==OP.DECLPROC:
            name,code = defs["name"],defs["code"]
            declarations[ name ] = code

        elif op==OP.CALLPROC:
            name = defs["name"]
            params=defs["params"]
            docs=defs["doc"]
            tests=defs["tests"]
            headers=defs["headers"]

            code = declarations[ name ]

            for p in params:
                for i in execute(code,pscope(scope,p)):
                    if i["OP"]=="HTTP":
                        yield {**i,
                            "doc": i["doc"]+docs,
                            "tests": i["tests"]+tests,
                            "headers": i["headers"]+headers,
                        }
                    elif i["OP"]=="WAIT":
                        yield i
                    else:
                        raise Exception(f"execute an unknown op '{op}'")

        else:
            raise Exception(f"execute an unknown op '{op}'")

#############################################################################

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
    - wait: <<j>>
    - GET: yolo
      params:
        p: p
- call: proc
  foreach: <<var>>
"""


    ll=compile(yaml.load(y))
    for i in ll:
        print(i)

    print(".............................")
    s=Scope(dict(
        root="http://root",
        headers={"x-me":"hello"},
        mymethod="return 42*3",
    ))
    for i in execute(ll, s):
        if i["OP"]=="WAIT":
            action="WAIT " + str(i["time"])
        else:
            action="HTTP "+i["method"]+" "+i["path"]
        print("==",action," IF "+str(i["IF"]), i)


