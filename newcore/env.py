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



def updateUrlQuery(url,d: dict):
    if d=={}:
        return url
    else:
        o=urllib.parse.urlparse(url)

        q=urllib.parse.parse_qs(o.query)
        for k,v in d.items():
            if v is None:
                if k in q:
                    del q[k]
            else:
                if type(v)==list:
                    q.setdefault(k,[]).extend(v)
                else:
                    q.setdefault(k,[]).append(v)

        o=o._replace(query=urllib.parse.urlencode( q , doseq=True))
        return o.geturl()


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
                        elem=resolver(elem)
                        if callable(elem):
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

        # create a Unique ID for this request
        uid = hashlib.md5()
        uid.update(
            json.dumps([self.method, self.path, self.body.decode(), self.inHeaders, self._tests_to_do, self._saves_to_do]).encode()
        )
        self.id = uid.hexdigest()


    @property
    def path(self):
        return urllib.parse.urlparse(self.url).path

    async def call(self, timeout=None, proxies=None, http=None) -> com.Response:
        t1 = datetime.datetime.now()

        if http is None:
            #real call on the web
            r = await com.call(self.method,self.url,self.body,self.inHeaders,timeout=timeout, proxies=proxies)
        else:
            #simulate with http hook
            r = com.call_simulation(http,self.method,self.url,self.body,self.inHeaders)

        diff = datetime.datetime.now() - t1
        self.time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)

        return r


    def treatment(self,env:dict, r:com.Response):
        assert isinstance(r,com.Response)

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

        repEnv=Scope(env) # clone
        repEnv.update(d)

        # saves
        new_vars={}
        for save_as,content in self._saves_to_do:
            try:
                v=repEnv.resolve_string_or_not(content)
                new_vars[save_as] = v
            except Exception as e:
                logging.debug(f"Can't resolve saved var '{save_as}', because {e}")
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
            test=testing.testCompare(var,val,expected)
            if self.status is None:
                test=test.toFalse()
            new_tests.append( test )


        del repEnv

        self.tests=new_tests
        self.saves=new_vars

    def __eq__(self, o):
        return o and self.id == o.id

    def __repr__(self):
        return "<Exchange: %s %s -> %s tests:%s>" % (
            self.method,
            self.url,
            self.status,
            self.tests or "no",
        )



def declare(code):
    return "def DYNAMIC(x,ENV):\n" + ("\n".join(["  " + i for i in code.splitlines()]))


def isPython(x):
    if type(x) == str and "return" in x:
        try:
            return compile(declare(x), "unknown", "exec") and True
        except:
            return False

def isJson(s:str):
    try:
        json.loads(s)
        return True
    except:
        pass


class Scope(dict): # like 'Env'

    def __init__(self,d,exposedsMethods={}):
        dict.__init__(self,d)

        # transform on pymethod's string in REAL pymethod's code
        for k,v in self.items():
            if v and isPython(v):
                exec(declare(v), globals())
                self[k]=DYNAMIC

        for k,v in exposedsMethods.items():
            if k not in self:
                self[k]=v

    #TODO: that (could replace "get_var")
    def resolve_all(self,obj,forceResolveOrException=True):
        if type(obj)!=str:
            obj=json.dumps(obj)

        obj= self.resolve_string(obj,forceResolveOrException)
        try:
            obj=json.loads(obj)
        except:
            pass

        return obj

    def resolve_string(self, txt:str, forceResolveOrException=True) -> str:
        """ replace all vars in the str
        raise ResolveException if can't
        """
        assert type(txt)==str, "wtf?"

        try:
            string=self._resolve_string(txt,forceResolveOrException)
            assert type(string)==str,"?!WTF"
            return string
        except RecursionError:
            raise ResolveException("Recursion trouble") # raise in all cases

    def _resolve_string(self, txt:str, forceResolveOrException=True) -> str:
        """ replace all vars in the str
        raise ResolveException if can't
        """
        find_vars=lambda txt: re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt)

        for pattern, content in [(i,i[2:-2]) for i in find_vars(txt) ]:
            value=self.get_var(content)

            # find a way to repr value as str -> v
            if value is NotFound:
                if forceResolveOrException:
                    raise ResolveException(f"can't resolve {pattern}")
                else:
                    v=pattern
            elif type(value) == bytes:
                try:
                    v = value.decode()
                except:
                    v = "".join(map(chr, value))    #TODO: (test 120)
            elif type(value) ==str:
                v = value
            else:
                try:
                    v=json.dumps(value)
                except:
                    v=str(value)

            # and replace
            logging.debug(f"replace in `{txt}` : `{pattern}` <- `{v}`")
            if f'"{pattern}"' in txt:
                if isJson(v):
                    txt=txt.replace( f'"{pattern}"', v )
                else:
                    txt=txt.replace( pattern, v )
            else:
                txt=txt.replace( pattern, v )
            logging.debug(f"replaced -> `{txt}`")

        if forceResolveOrException and find_vars(txt):
            txt=self._resolve_string(txt)

        return txt

    def resolve_string_or_not(self,obj: object) -> object:
        """ like resolve() but any type in/out, without exception """
        if type(obj)==str:
            obj = self.resolve_all( obj , forceResolveOrException=False)

        return obj

    def get_var(self,vardef: str): # -> any or NotFound
        """ resolve content of the var (can be "var.var.size", or "var|fct|fct")
            return value or NotFound
            can raise PyMethodException
        """
        assert type(vardef)==str

        if "|" in vardef:
            var, *methods = vardef.split("|")
            # when xpath, there can be "|" in var ...
            # so we try to let them in place ;-)
            while len(methods)>0 and methods[0].startswith("/"): #assuming xpath part starts with "/"
                m=methods.pop(0)
                var+="|"+m
        else:
            var, methods =vardef, []


        if var=="": # case of <<|fct>> (historic way)
            value=None
        else:
            isIgnorable=False

            if var.endswith("?"):
                var=var[:-1]
                isIgnorable=True

            value = jpath(self,var)

            if type(value)==str:
                # resolve value content, before applying methods
                value = self.resolve_string_or_not( value )

            if (value is NotFound) and isIgnorable:
                value=""

        if value is not NotFound:
            # and apply methods on the value
            for method in methods:
                if method in self:
                    callabl=self[method]
                    value=self.run(callabl,value)
                else:
                    return NotFound

        return value


    def get_var_or_empty(self,vardef: str) -> str:
        assert type(vardef)==str

        value = self.get_var(vardef)
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
        if not callable(method):
            raise PyMethodException(f"Can't call '{method}' : unknown one ?")
        try:
            return method(value,self)
        except Exception as e:
            raise PyMethodException(f"Can't call '{method.__name__}' : {e}")


    async def call(self, method:str, path:str, headers:dict={}, body:str="", saves=[], tests=[], doc:str="", timeout=None, querys={}, proxies=None, http=None) -> Exchange:
        assert type(body)==str
        assert all( [type(i)==tuple and len(i)==2 for i in tests] ) # assert list of tuple of 2
        assert all( [type(i)==tuple and len(i)==2 for i in saves] ) # assert list of tuple of 2

        try:
            # use global headers and merge them in headers
            gheaders = self.get("headers", None)  # global headers
            if gheaders is not None:
                if type(gheaders) == str:
                    gheaders = self.resolve_all(gheaders)

                    if type(gheaders)!=dict:
                        raise ResolveException("global headers are not resolved as a dict")
                else:
                    gheaders=dict(gheaders) # clone

                # merge current headers in gheaders
                gheaders.update( {k:v for k,v in headers.items()} )
                headers=gheaders


            # update path, with potentials "query" defs
            pquerys={}
            for k,v in querys.items():
                if v is None:
                    pquerys[k]=None
                elif type(v)==list:
                    ll=[]
                    for i in v:
                        if i is not None:
                            i=self.resolve_all(i)
                            if type(i)==list:
                                ll.extend(i)
                            else:
                                ll.append(i)

                    pquerys[k]=ll
                else:
                    pquerys[k]=self.resolve_all(v)

            path=updateUrlQuery(path,pquerys)


            path=self.resolve_string(path)
            if not urllib.parse.urlparse(path).scheme:
                path=self.get_var_or_empty("root")+path
            body=self.resolve_string(body)
            headers={k:self.resolve_string(str(v)) for k,v in headers.items() if v is not None} # remove headers valuated as None
            r=None
        except ResolveException as e:
            #can't resolve, so can't make http request, so all tests are ko
            r=com.ResponseError(f"Request can't be resolved: {e}")
        except PyMethodException as e:
            #a conf trouble .... break the rule !
            r=com.ResponseError(f"Python Method in error: {e}")


        ex=Exchange(method,path,body.encode(),headers, tests=tests, saves=saves, doc=doc)
        if r is None: # we can call it safely
            r=await ex.call(timeout,proxies=proxies,http=http)

        ex.treatment( self, r)

        return ex





if __name__=="__main__":
    import pytest

    logging.basicConfig(level=logging.DEBUG)

    env=Scope(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    # with pytest.raises(PyMethodException):
    #     e.resolve("a txt <<upper>>")    # this method use the param !

    # with pytest.raises(ResolveException):
    #     e.resolve("a txt <<unknwon>>")  # unknown method

    tests=[
        ("status","<<v200>>"),
        ("status",".>= {{v200}}"),
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




