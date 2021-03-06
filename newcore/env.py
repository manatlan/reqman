#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import json
import datetime
import urllib.parse
import hashlib
import logging

try:
    from newcore.common import NotFound,decodeBytes,jdumps
    import newcore.com as com
    import newcore.testing as testing
    import newcore.xlib as xlib
except ModuleNotFoundError:
    from common import NotFound,jdumps,decodeBytes
    import com
    import testing
    import xlib

import typing as T

class PyMethodException(Exception): pass
class ResolveException(Exception): pass




def jpath(elem, path: str) -> T.Union[int, T.Type[NotFound], str]:
    runner=elem.run
    resolver=elem.resolve_string_or_not
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

                    if elem is not NotFound:
                        # NOT TOP /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
                        if type(elem)==str and "<<" in elem:
                            elem=resolver(elem)

                            try:
                                elem= json.loads(elem)
                            except:
                                pass

                        elif callable(elem):
                            elem=runner(elem,None)
                        # NOT TOP /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

            elif type(elem) == str:
                if i == "size":
                    return len(elem)
                elif i.isnumeric() or i.startswith("-"):
                    elem= elem[ int(i) ]
                else:
                    return NotFound

            elif type(elem)==xlib.Xml:
                elem=elem.xpath(i)

        except (ValueError, IndexError) as e:
            return NotFound
    return elem



class Exchange:
    def __init__(self,method: str,url: str,body: bytes=b"",headers: dict={}, tests:list=[], saves:list=[], doc:str = ""):
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
        self.doc=doc

        #TODO:
        self.nolimit=True

        # internals
        self._tests_to_do=tests
        self._saves_to_do=saves


    @property
    def path(self):
        return urllib.parse.urlparse(self.url).path

    async def call(self, env:dict, timeout=None,http=None):
        t1 = datetime.datetime.now()

        if http is None:
            #real call on the web
            r = await com.call(self.method,self.url,self.body,self.inHeaders,timeout=timeout)
        else:
            #simulate with http hook
            #####################################################################"
            status, content, outHeaders = ( # default response 404
                404,
                "mock not found",
                {"server": "reqman mock"},
            )

            if self.url in http:
                rep = http[self.url]
                try:
                    if callable(rep):
                        rep = rep(self.method, self.url, self.body, self.inHeaders)

                    if len(rep) == 2:
                        status, content = rep
                    elif len(rep) == 3:
                        status, content, oHeaders = rep
                        outHeaders.update( oHeaders )
                    else:
                        raise Exception("Bad mock response")
                except Exception as e:
                    status, content = 500, f"mock server error: {e}"
                assert type(content) in [str, bytes]
                assert type(status) is int
                assert type(outHeaders) is dict

            info=f"MOCK/1.0 {status} RESPONSE"


            # ensure content is bytes
            content = content.encode() if type(content)==str else content
            logging.debug(f"Simulate {self.method} {self.url} --> {status}")
            r=com.Response(status,outHeaders,content,info)
            #####################################################################"

        diff = datetime.datetime.now() - t1
        self.time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)

        self.treatment(env,r)


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


        def get_json():# -> any
            try:
                return json.loads(self.content.decode())
            except:
                return None

        def get_xml():
            try:
                return xlib.Xml(self.content.decode())
            except:
                return None


        # creating an Env for testing and saving
        resp=dict(
            status=self.status,
            headers=testing.HeadersMixedCase(**self.outHeaders),
            content=self.content, #bytes
            json=get_json(),
            xml=get_xml(),
            time=self.time,
        )

        d={}
        d.update( resp)
        d["request"] = dict( method=self.method, url=self.url, headers=testing.HeadersMixedCase(**self.inHeaders), body=self.body)
        d["response"] = resp

        d["rm"]=dict(response=d["response"],request=d["request"])

        repEnv=Env(env) # clone
        repEnv.update(d)

        # saves
        new_vars={}
        for save_as,content in self._saves_to_do:
            try:
                v=repEnv.resolve_string_or_not(content)
                try:
                    v= json.loads(v)
                except:
                    pass
                new_vars[save_as] = v
            except Exception as e:
                logging.warn(f"Can't resolve saved var '{save_as}', because {e}")
                new_vars[save_as]= content # create a non-resolved var'string (<<example>>)

        # Save all in this env, to be visible in tests later (vv)
        repEnv.update( new_vars)

        # update the doc'string
        self.doc = repEnv.resolve_string_or_not(self.doc)

        # tests
        new_tests=[]
        for var,expected in self._tests_to_do:
            expected=repEnv.resolve_string_or_not(expected)
            val=repEnv.get_var_or_empty(var)
            new_tests.append( testing.testCompare(var,val,expected) )


        del repEnv

        self.tests=new_tests
        self.saves=new_vars

class Env(dict):
    def __init__(self,d,exposedsMethods={}):
        dict.__init__(self,d)
        for k,v in exposedsMethods.items():
            if k not in self:
                self[k]=v


    def resolve_string(self, txt:str, notFoundException=True) -> str:
        """ replace all vars in the str
        raise ResolveException if can't
        """
        try:
            string=self._resolve_string(txt,notFoundException)
            assert type(string)==str,"?!WTF"
            return string
        except RecursionError:
            raise ResolveException()

    def _resolve_string(self, txt:str, notFoundException=True) -> str:
        """ replace all vars in the str
        raise ResolveException if can't
        """
        find_vars=lambda txt: re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt)

        for pattern, content in [(i,i[2:-2]) for i in find_vars(txt) ]:
            value=self.get_var(content)
            if value is NotFound:
                if notFoundException:
                    raise ResolveException()
                else:
                    value=pattern
            if type(value) == bytes:
                txt=txt.replace( pattern, value.decode() )
            elif type(value) ==str:
                txt=txt.replace( pattern, value )
            else:
                try:
                    v=json.dumps(value)
                except:
                    v=str(v)
                txt=txt.replace( pattern, v )

        if notFoundException and find_vars(txt):
            txt=self._resolve_string(txt)

        return txt

    def resolve_string_or_not(self,txt: object) -> object:
        """ like resolve() but any type in/out, without exception """
        if type(txt)==str:
            txt = self.resolve_string( str(txt) ,notFoundException=False)

        return txt

    def get_var(self,content: str): # -> any or NotFound
        """ resolve content of the var (can be "var.var.size", or "var|fct|fct")
            return value or NotFound
            can raise PyMethodException
        """
        if "|" in content:
            var, *methods = content.split("|")
            # when xpath, there can be "|" in var ...
            # so we try to let them in place ;-)
            while len(methods)>0:
                if methods[0].startswith("/"): #assuming xpath part starts with "/"
                    m=methods.pop(0)
                    var+="|"+m
                else:
                    break
        else:
            var, methods =content, []

        if var=="": # case of <<|fct>>
            value=None
        else:
            value = jpath(self,var)

            if type(value)==str:
                # resolve value content, before applying methods
                value = self.resolve_string_or_not( value )

        # and apply methods on the value
        if methods and value is not NotFound:
            for method in methods:
                if method in self:
                    callabl=self[method]
                    value=self.run(callabl,value)
                else:
                    return NotFound

        # try to remake an object (if value was json serialized one)
        try:
            return json.loads(value)
        except:
            return value


    def get_var_or_empty(self,content: str) -> str:
        value = self.get_var(content)
        if value is NotFound:
            return ""
        else:
            if type(value)==bytes:
                return decodeBytes(value)
            else:
                if type(value) in [list,dict]:
                    return jdumps(value)
                else:
                    return str(value)


    def run(self,method: T.Callable , value):
        try:
            return method(value,self)
        except:
            raise PyMethodException()


    async def call(self, method:str, path:str, headers:dict={}, body:str="", saves=[], tests=[], doc:str="", timeout=None,http=None) -> Exchange:
        assert type(body)==str
        assert all( [type(i)==tuple and len(i)==2 for i in tests] ) # assert list of tuple of 2
        assert all( [type(i)==tuple and len(i)==2 for i in saves] ) # assert list of tuple of 2

        if not urllib.parse.urlparse(path.lower()).scheme:
            path=self.get_var_or_empty("root")+path

        try:
            path=self.resolve_string(path)
            body=self.resolve_string(body)
            headers={k:self.resolve_string(str(v)) for k,v in headers.items()}
            r=None
        except ResolveException:
            #can't resolve, so can't make http request, so all tests are ko
            r=com.ResponseError("Path/body/headers non resolved")
        except PyMethodException:
            #a conf trouble .... break the rule !
            r=com.ResponseError("Python Method in error")


        ex=Exchange(method,path,body.encode(),headers, tests=tests, saves=saves, doc=doc)
        if r is None: # we can call it safely
            await ex.call(self,timeout,http=http)
        else:
            ex.treatment( self, r)

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




