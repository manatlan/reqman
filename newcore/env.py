#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import json
import datetime
import urllib.parse
import hashlib

try:
    from . import com
    from . import utils
except:
    import com
    import utils

import typing as T

class NotFound: pass
class PyMethodException(Exception): pass
class ResolveException(Exception): pass




def jpath(elem, path: str) -> T.Union[int, T.Type[NotFound], str]:
    runner=elem.run
    for i in path.strip(".").split("."):
        try:
            if elem is None:
                return NotFound

            elif type(elem) == list:
                if i == "size":
                    return len(elem)
                else:
                    elem = elem[int(i)]
            elif isinstance(elem, dict):
                if i == "size":
                    return len(list(elem.keys()))
                else:
                    elem = elem.get(i, NotFound)

                    if elem is not NotFound and callable(elem):
                        elem=runner(elem,None)

            elif type(elem) == str:
                if i == "size":
                    return len(elem)
                elif i.isnumeric() or i.startswith("-"):
                    elem= elem[ int(i) ]
                else:
                    return NotFound


        except (ValueError, IndexError) as e:
            return NotFound
    return elem



class Exchange:
    def __init__(self,method: str,url: str,body: bytes=b"",headers: dict={}, tests:list=[],saves:list=[]):
        assert type(body)==bytes


        # inputs
        self.method=method
        self.url=url
        self.body=body
        self.inHeaders=headers

        # outputs
        self.status=0
        self.outHeaders={}
        self.content=b''
        self.info=""
        self.time=0

        # more outputs
        self.tests=[]
        self.saves={}
        self.id=None

        #TODO:
        self.nolimit=True
        self.doc=""

        # internals
        self._tests_to_do=tests
        self._saves_to_do=saves


    @property
    def path(self):
        return urllib.parse.urlparse(self.url).path


    @property #TODO
    def bodyContent(self):
        return self.content

    async def call(self, env:dict):
        t1 = datetime.datetime.now()

        r = await com.call(self.method,self.url,self.body,self.inHeaders)
        self.treatment(env,r)

        diff = datetime.datetime.now() - t1
        self.time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)

    def treatment(self,env:dict, r:com.Response):
        assert isinstance(r,com.Response)

        # create a Unique ID for this request
        uid = hashlib.md5()
        uid.update(
            json.dumps([self.method, self.path, self.body.decode(), self.inHeaders, self._tests_to_do, self._saves_to_do]).encode()
        )

        self.id = uid.hexdigest()


        self.status=r.status
        self.outHeaders=dict(r.headers)
        self.content=r.content
        self.info=r.info

        # if isinstance(r,com.ResponseError):
        #     # can't get a correct response, don't do tests & saves
        #     #TODO: coninue here
        #     pass
        # else:

        # creating an Env for testing and saving
        resp=dict(
            status=self.status,
            headers=utils.HeadersMixedCase(**self.outHeaders),
            content=self.content, #bytes
            json=r.get_json(),
            xml=r.get_xml(),
        )

        d={}
        d.update( resp)
        d["request"] = dict( method=self.method, url=self.url, headers=utils.HeadersMixedCase(**self.inHeaders), body=self.body)
        d["response"] = resp

        d["rm"]=dict(response=d["response"],request=d["request"])

        repEnv=Env(env) # clone
        repEnv.update(d)

        # tests
        new_tests=[]
        for var,expected in self._tests_to_do:
            expected=repEnv.resolve_or_not(expected)
            val=repEnv.resolve_var_or_empty(var)
            new_tests.append( utils.testCompare(var,val,expected) )

        # saves
        new_vars={}
        for save_as,content in self._saves_to_do:
            new_vars[save_as] = repEnv.resolve_or_not(content)

        del repEnv

        self.tests=new_tests
        self.saves=new_vars

class Env(dict):
    def __init__(self,d):
        dict.__init__(self,d)

    def resolve(self, txt:str, nb_rec=0) -> str:
        """ replace all vars in the str
        raise ResolveError if can't
        """
        find_vars=lambda txt: re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt)

        for pattern, content in [(i,i[2:-2]) for i in find_vars(txt) ]:
            value=self.resolve_var(content)
            if value is NotFound:
                raise ResolveException()
            txt=txt.replace( pattern, str(value) )

        if find_vars(txt):
            if nb_rec>10:
                raise ResolveException() # avoid recursion !
            else:
                txt=self.resolve(txt,nb_rec+1)

        return txt

    def resolve_or_not(self,txt: object) -> object:
        """ like resolve() but any type in/out, without exception """
        if type(txt)==str:
            try:
                txt=self.resolve( str(txt) )
            except ResolveException:
                txt=txt

        return txt

    def resolve_var(self,content: str): # -> any or NotFound
        """ resolve content of the var (can be "var.var.size", or "var|fct|fct")
            return value or NotFound
            can raise PyMethodException
        """
        if "|" in content:
            var, *methods = content.split("|")
        else:
            var, methods =content, []

        value = jpath(self,var)

        if methods and value is not NotFound:
            for method in methods:
                if method in self:
                    callabl=self[method]
                    value=self.run(callabl,value)
                else:
                    return NotFound

        return value


    def resolve_var_or_empty(self,content: str) -> str:
        value = self.resolve_var(content)
        if value is NotFound:
            return ""
        else:
            return str(value)


    def run(self,method: T.Callable , value):
        try:
            return method(value,self)
        except:
            raise PyMethodException()


    async def call(self, method:str, path:str, headers:dict={}, body:str="", saves=[], tests=[]) -> Exchange:
        assert type(body)==str
        assert all( [type(i)==tuple and len(i)==2 for i in tests] ) # assert list of tuple of 2
        assert all( [type(i)==tuple and len(i)==2 for i in saves] ) # assert list of tuple of 2

        if not urllib.parse.urlparse(path.lower()).scheme:
            path=self.resolve_var_or_empty("root")+path

        try:
            path=self.resolve(path)
            body=self.resolve(body)
            headers={k:self.resolve(str(v)) for k,v in headers.items()}
        except ResolveException:
            #can't resolve, so can't make http request, so all tests are ko
            #TODO: coninue here
            pass
        except PyMethodException:
            #a conf trouble .... break the rule !
            #TODO: coninue here
            pass

        ex=Exchange(method,path,body.encode(),headers, tests=tests, saves=saves)
        await ex.call(self)
        return ex






if __name__=="__main__":
    import pytest

    env=Env(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    # with pytest.raises(PyMethodException):
    #     e.resolve("a txt <<upper>>")    # this method use the param !

    # with pytest.raises(ResolveException):
    #     e.resolve("a txt <<unknwon>>")  # unknown method

    tests=[
        ("status","<<v200>>"),
        ("status",".>= <<v200>>"),
        ("status",".> 100"),
        ("response.status",200),
        ("json.items.size",".> 2"),
        ("json.value|upper","HELLO"),
        ("response.json.items.size",3),
        ("rm.response.json.items.size",3),
        ("request.method","GET"),
        ("rm.request.method|upper","GET"),
        ("response.headers.x-test","hello"),
        ("rm.response.headers.X-TeSt|upper","HELLO"),
        ("unknwon|upper",None),
    ]
    saves=[
        ("hello","<<status>>"),
        ("js","<<response.json>>"),
        ("ll","<<response.json.items>>"),
        ("val","<<response.json.items.1>>"),
        ("MAX","<<response.json.value|upper>>"),
        ("nimp","<<nimp>>"),
    ]

    ex=Exchange("GET","/", tests=tests, saves=saves)

    obj= dict(items=list("abc"),value="hello")
    r=com.Response(200,{"x-test":"hello"},json.dumps(obj).encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)
    #     print(r)




