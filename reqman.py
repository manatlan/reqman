#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018 manatlan manatlan[at]gmail(dot)com
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

import yaml         # see "pip install pyaml"
import encodings
import os
import json
import string
import sys
import ssl
import glob
import html as cgi
import socket
import re
import copy
import collections
import io
import datetime
import email
import xml.dom.minidom
import http.cookies
import http.cookiejar
import http.client
import urllib.request
import urllib.parse
import urllib.error

class NotFound: pass
class RMException(Exception):pass

__version__="0.9.9.2"
REQMAN_CONF="reqman.conf"

###########################################################################
## Utilities
###########################################################################
try: # colorama is optionnal
    from colorama import init,Fore,Style
    init()

    cy=lambda t: Fore.YELLOW+Style.BRIGHT + t + Fore.RESET+Style.RESET_ALL if t else None
    cr=lambda t: Fore.RED+Style.BRIGHT + t + Fore.RESET+Style.RESET_ALL if t else None
    cg=lambda t: Fore.GREEN+Style.BRIGHT + t + Fore.RESET+Style.RESET_ALL if t else None
    cb=lambda t: Fore.CYAN+Style.BRIGHT + t + Fore.RESET+Style.RESET_ALL if t else None
    cw=lambda t: Fore.WHITE+Style.BRIGHT + t + Fore.RESET+Style.RESET_ALL if t else None
except:
    cy=cr=cg=cb=cw=lambda t: t


def yamlLoad(fd):    # fd is an io thing
    b=fd.read()
    if type(b)==bytes:
        try:
            b=str(b,"utf8")
        except:
            b=str(b,"cp1252")
    return yaml.load( b )


def dict_merge(dct, merge_dct):
    """ merge 'merge_dct' in --> dct """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            if (k in dct and isinstance(dct[k], list) and isinstance(merge_dct[k], list)):
                dct[k] += merge_dct[k]
            else:
                dct[k] = merge_dct[k]


def prettify(txt,indentation=4):
    try:
        x=xml.dom.minidom.parseString( txt ).toprettyxml(indent=" "*indentation)
        x="\n".join([s for s in x.splitlines() if s.strip()]) # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/
        return x
    except:
        try:
            return json.dumps( json.loads( txt ), indent=indentation, sort_keys=True )
        except:
            return txt



def jpath(elem, path):
    for i in path.strip(".").split("."):
        try:
            if type(elem)==list:
                if i=="size":
                    return len(elem)
                else:
                    elem= elem[ int(i) ]
            elif type(elem)==dict:
                if i=="size":
                    return len(list(elem.keys()))
                else:
                    elem= elem.get(i,NotFound)
        except (ValueError,IndexError) as e:
            return NotFound
    return elem



###########################################################################
## http request/response
###########################################################################

class CookieStore(http.cookiejar.CookieJar):
    """ Manage cookiejar for httplib-like """
    def saveCookie(self,headers,url):
        if type(headers)==dict: headers=list(headers.items())

        class FakeResponse:
            def __init__(self, headers=[], url=None):
                """
                headers: list of RFC822-style 'Key: value' strings
                """
                m = email.message_from_string( "\n".join(headers) )
                self._headers = m
                self._url = url
            def info(self): return self._headers


        response = FakeResponse( [ ": ".join([k,v]) for k,v in headers], url )
        self.extract_cookies(response, urllib.request.Request(url) )

    def getCookieHeaderForUrl(self,url):
        r=urllib.request.Request(url)
        self.add_cookie_header(r)
        return dict(r.header_items())

COOKIEJAR = CookieStore()

class Request:
    def __init__(self,protocol,host,port,method,path,body=None,headers={}):

        self.protocol=protocol
        self.host=host
        self.port=port
        self.method=method
        self.path=path
        self.body=body
        self.headers={}

        if self.protocol:
            self.url="%s://%s%s" % (
                self.protocol,
                (self.host or "")+(":%s"%self.port if self.port else ""),
                self.path
            )

            self.headers = COOKIEJAR.getCookieHeaderForUrl( self.url )
        else:
            self.url=None

        self.headers.update(headers)

    def __repr__(self):
        return cy(self.method)+" "+self.path

class Content:
    def __init__(self,content):
        self.__b=content if type(content)==bytes else bytes( content,"utf8" )

    def toBinary(self):
        return self.__b

    def __repr__(self):
        try:
            return str(self.__b,"utf8") # try as utf8 ...
        except:
            try:
                return str(self.__b,"cp1252")  # try as cp1252 ...
            except:
                # fallback to a *** binary representation ***
                return "*** BINARY SIZE(%s) ***" % len(self.__b)

    def __contains__(self, key):
        return key in str(self)


class Response:
    def __init__(self,status,body,headers,url):
        self.status = status
        self.content = Content(body)
        self.headers = dict(headers)    # /!\ cast list of 2-tuple to dict ;-(
                                        # eg: if multiple "set-cookie" -> only the last is kept
        COOKIEJAR.saveCookie( headers, url )

    def __repr__(self):
        return "%s" % (self.status)

class ResponseError:
    def __init__(self,m):
        self.status = None
        self.content = m
        self.headers = {}
    def __repr__(self):
        return "ERROR: %s" % (self.content)


def dohttp(r):
    try:
        if r.protocol and r.protocol.lower()=="https":
            cnx=http.client.HTTPSConnection(r.host,r.port,context=ssl._create_unverified_context()) #TODO: ability to setup a verified ssl context ?
        else:
            cnx=http.client.HTTPConnection(r.host,r.port)
        enc=lambda x: x.replace(" ","%20")
        cnx.request(r.method,enc(r.path),r.body,r.headers)
        rr=cnx.getresponse()
        return Response( rr.status,rr.read(),rr.getheaders(), r.url )
    except socket.timeout:
        #raise RMException("Server is down (%s)?" % ((r.host+":%s" % r.port) if r.port else r.host))
        return ResponseError("Response timeout")
    except socket.error:
        #raise RMException("Server is down (%s)?" % ((r.host+":%s" % r.port) if r.port else r.host))
        return ResponseError("Server is down ?!")
    except http.client.BadStatusLine:
        #A subclass of HTTPException. Raised if a server responds with a HTTP status code that we don’t understand.
        #Presumably, the server closed the connection before sending a valid response.
        # raise RMException("Server closed the connection (%s)?" % ((r.host+":%s" % r.port) if r.port else r.host))
        return ResponseError("Server closed the connection")



###########################################################################
## Reqs manage
###########################################################################

class Test(int):
    """ a boolean with a name """
    def __new__(cls, value,nameOK,nameKO):
        s=super(Test, cls).__new__(cls, value)
        if value:
            s.name = nameOK
        else:
            s.name = nameKO
        return s

class TestResult(list):
    def __init__(self,req,res,tests):
        self.req=req
        self.res=res

        insensitiveHeaders= {k.lower():v for k,v in self.res.headers.items()} if self.res else {}

        results=[]
        for test in tests:
            what,value = list(test.keys())[0],list(test.values())[0]

            canMatchAll=False
            #------------- find the cmp method
            if what=="content":     cmp = lambda x: x in str(self.res.content)
            elif what=="status":    cmp = lambda x: int(x)==(self.res.status and int(self.res.status))
            elif what.startswith("json."):
                canMatchAll=True
                try:
                    jzon=json.loads( str(self.res.content) )
                    v=jpath(jzon,what[5:])
                    v=None if v == NotFound else v

                    cmp = lambda x: x == v
                except:
                    cmp = lambda x: False
            else:
                cmp = lambda x: x in insensitiveHeaders.get(what.lower(),"")    #TODO: test if header is just present
            #-------------

            if type(value)==list:
                if canMatchAll:
                    matchAll=cmp(value)
                    val = " ,".join( [str(i) for i in value] )
                    if matchAll:
                        testname = "%s = [%s]" % (what,val)
                        testnameKO = "%s != [%s]" % (what,val)
                        result = matchAll
                    else:
                        testname = "%s in [%s]" % (what,val)
                        testnameKO = "%s not in [%s]" % (what,val)
                        result = any( [cmp(i) for i in value] ) or matchAll
                else:
                    val = " ,".join( [str(i) for i in value] )
                    testname = "%s in [%s]" % (what,val)
                    testnameKO = "%s not in [%s]" % (what,val)
                    result = any( [cmp(i) for i in value] )
            else:
                val = "null" if value is None else "true" if value is True else "false" if value is False else value
                testname = "%s = %s" % (what,val)
                testnameKO = "%s != %s" % (what,val)
                result = cmp(value)

            results.append( Test(result,testname,testnameKO) )

        list.__init__(self,results)

    def __repr__(self):
        ll=[""]
        ll.append( cy("*")+" %s --> %s" % (self.req,cw(str(self.res)) if self.res else cr("Not callable") ))
        for t in self:
            ll.append( "  - %s: %s" % ( cg("OK") if t==1 else cr("KO"),t.name ) )
        txt = "\n".join(ll)
        return txt

def getVar(env,var):
    if var in env:
        return txtReplace(env,env[var])
    elif "|" in var:
        key,method=var.split("|",1)

        content = env.get(key,key)     # resolv keys else use it a value !!!!!
        content=txtReplace(env,content)
        for m in method.split("|"):
            content=transform(content,env,m)
            content=txtReplace(env,content)
        return content

    elif "." in var:
        val=jpath(env,var)
        if val is NotFound:
            raise RMException("Can't resolve "+var+" in : "+ ", ".join(list(env.keys())))
        return txtReplace(env,val)
    else:
        raise RMException("Can't resolve "+var+" in : "+ ", ".join(list(env.keys())))



def transform(content,env,methodName):
    if methodName:
        if methodName in env:
            code=getVar(env,methodName)
            try:
                exec("def DYNAMIC(x,ENV):\n" + ("\n".join(["  "+i for i in code.splitlines()])), globals())
            except Exception as e:
                raise RMException("Error in declaration of method "+methodName+" : "+str(e))
            try:
                x=json.loads(content)
            except:
                x=content
            try:
                if transform.path:
                    curdir = os.getcwd()
                    os.chdir( transform.path )
                content=DYNAMIC( x,env )
            except Exception as e:
                raise RMException("Error in execution of method "+methodName+" : "+str(e))
            finally:
                if transform.path:
                    os.chdir(curdir)
        else:
            raise RMException("Can't find method "+methodName+" in : "+ ", ".join(list(env.keys())))

    return content

transform.path=None # change cd cwd for transform methods when executed


def objReplace(env,txt): # same as txtReplace() but for "object" (json'able)
    obj=txtReplace(env,txt)
    try:
        obj=json.loads(obj)
    except:
        pass
    return obj

def txtReplace(env,txt):
    if env and txt and isinstance(txt,str):
        for vvar in re.findall("\{\{[^\}]+\}\}",txt)+re.findall("<<[^>]+>>",txt):
            var=vvar[2:-2]

            try:
                val=getVar(env,var)   #recursive here ! (if myvar="{{otherVar}}"", redo a pass to resolve otherVar)
            except RuntimeError:
                raise RMException("Recursion trouble for '%s'" % var)

            if val is NotFound:
                raise RMException("Can't resolve "+var+" in : "+ ", ".join(list(env.keys())))
            else:
                if type(val) != str:
                    if val is None:
                        val=""
                    elif val is True:
                        val="true"
                    elif val is False:
                        val="false"
                    elif type(val) in [list,dict]:
                        val=json.dumps(val)
                    elif type(val) == bytes:
                        val=str(val,"utf8") #TODO: good ? NEED MORE TESTS !!!!!
                    else: #int, float, ...
                        val=json.dumps(val)

                #~ txt=txt.replace( vvar , str(val, "utf-8") if type(val)!=str else val )
                txt=txt.replace( vvar , val )

    return txt

def warn(*m):
    print("***WARNING***",*m)

def getTests(y):
    """ Get defined tests as list ok dict key:value """
    if y:
        tests=y.get("tests",[])
        if type(tests)==dict:
             warn("'tests:' should be a list of mono key/value pairs (ex: '- status: 200')")
             tests = [ {k:v} for k,v in tests.items()]

        return tests
    else:
        return []

def getHeaders(y):
    """ Get defined headers as dict """
    if y:
        headers=y.get("headers",{})
        if type(headers)==list:
             warn("'headers:' should be filled of key/value pairs (ex: 'Content-Type: text/plain')")
             headers= { list(d.keys())[0]:list(d.values())[0] for d in headers}

        return headers
    else:
        return {}



class Req(object):
    def __init__(self,method,path,body=None,headers={},tests=[],saves=[],params={}):  # body = str ou dict ou None
        self.method=method.upper()
        self.path=path
        self.body=body
        self.headers=headers
        self.tests=tests
        self.saves=saves
        self.params=params

    def test(self,env=None):
        cenv = env.copy() if env else {}    # current env
        cenv.update( self.params )          # override with self params

        # path ...
        path = txtReplace(cenv,self.path)
        if cenv and (not path.strip().lower().startswith("http")) and ("root" in cenv):
            h=urllib.parse.urlparse( cenv["root"] )
            if h.path and h.path[-1]=="/":
                if path[0]=="/":
                    path=h.path + path[1:]
                else:
                    path=h.path + path
            else:
                path=h.path + path
        else:
            h=urllib.parse.urlparse( path )
            path = h.path + ("?"+h.query if h.query else "")

        # headers ...
        headers=getHeaders(cenv).copy() if cenv else {}
        headers.update(self.headers)                        # override with self headers

        headers={ k:txtReplace(cenv,v) for k,v in list(headers.items()) if v is not None}

        # body ...
        if self.body and not isinstance(self.body,str):

            def jrep(x): # "json rep"
                return objReplace(cenv,x)

            #================================
            def apply(body,method):
                if type(body)==list:
                    return [ apply(i,method) for i in body]
                elif type(body)==dict:
                    return { k:apply(v,method) for k,v in body.items() }
                else:
                    return method(body)
            #================================

            body=apply( self.body, jrep )
            body=json.dumps( body ) # and convert to string !
        else:
            body=txtReplace(cenv,self.body)

        req=Request(h.scheme,h.hostname,h.port,self.method,path,body,headers)
        if h.hostname:

            tests=getTests(cenv)
            tests+=self.tests                               # override with self tests

            ntests=[]
            for test in tests:
                key,val = list(test.keys())[0],list(test.values())[0]
                if type(val)==list:
                    val=[txtReplace(cenv,i) for i in val]
                else:
                    val=txtReplace(cenv,val)
                ntests.append( {key: val } )
            tests=ntests

            timeout=cenv.get("timeout",None)
            try:
                socket.setdefaulttimeout( timeout and float(timeout)/1000.0 )
            except ValueError:
                socket.setdefaulttimeout( None )

            t1=datetime.datetime.now()
            res=dohttp( req )
            res.time=datetime.datetime.now()-t1
            if isinstance(res,Response) and self.saves:

                self.saves=self.saves if type(self.saves)==list else [self.saves] # ensure we've got a list

                for save in self.saves:
                    dest=txtReplace(cenv,save)
                    if dest.lower().startswith("file://"):
                        name=dest[7:]
                        try:
                            with open(name,"wb+") as fid:
                                fid.write(res.content.toBinary())
                        except Exception as e:
                            raise RMException("Save to file '%s' error : %s" % (name,e))
                    else:
                        if dest:
                            try:
                                env[ dest ]=json.loads(str(res.content))
                                cenv[ dest ]=json.loads(str(res.content))
                            except:
                                env[ dest ]=str(res.content)
                                cenv[ dest ]=str(res.content)

            return TestResult(req,res,tests)
        else:
            # no hostname : no response, no tests ! (missing reqman.conf the root var ?)
            return TestResult(req,None,[])

    def __repr__(self):
        return "<%s %s>" % (self.method,self.path)

class Reqs(list):
    def __init__(self,fd,env=None):
        self.env=env or {}    # just for proc finding
        self.name = fd.name.replace("\\","/") if hasattr(fd,"name") else "String"
        if not hasattr(fd,"name"): setattr(fd,"name","<string>")
        try:
            l=yamlLoad(fd)
        except Exception as e:
            raise RMException("YML syntax in %s\n%s"%(fd.name or "<string>",e))

        procedures={}

        def feed(l):
            """ recursive, return a list of <Req> (valids)"""
            KNOWNVERBS = set(["GET","POST","DELETE","PUT","HEAD","OPTIONS","TRACE","PATCH","CONNECT"])
            ll=[]

            if l:
                l=[l] if type(l)==dict else l # ensure we've got a list

                for d in l:
                    env={}
                    dict_merge(env,self.env)
                    dict_merge(env,d.get("params",{}))  # add current params (to find proc)

                    if "call" in list(d.keys()):
                        callContent=objReplace(env,d["call"])

                        callnames = callContent if type(callContent)==list else [ callContent ]   # make a list ;-)
                        del d["call"]

                        for callname in callnames:
                            commands = procedures[callname] if callname in procedures else self.env[callname] if callname in self.env else None # local proc in first !

                            if commands:
                                commands=[commands] if type(commands)==dict else commands # ensure we've got a list

                                ncommands=[]
                                for command in commands:
                                    q = copy.deepcopy( command )
                                    if KNOWNVERBS.intersection( list(q.keys()) ) or "call" in list(q.keys()):
                                        # merge passed params with action only ! (avoid merging with proc declaration)
                                        dict_merge(q,d)
                                    ncommands.append( q )
                                ll+=feed(ncommands)    # *recursive*

                                continue
                            else:
                                raise RMException("call a not defined procedure '%s' in '%s'" % (callname,fd.name))
                        continue
                    elif len(list(d.keys()))==1: # a declaration of a procedure ?
                        callname=list(d.keys())[0]
                        if type(d[callname]) in [dict,list]:    # dict is one call, list is a list of dict (multiple calls) -> so it's a procedure
                            procedures[callname] = d[callname]        # save it
                            continue  # just declare and nothing yet
                        else:
                            # it's, perhaps, a single command (ex: "- GET: /")
                            pass

                    verbs=list(KNOWNVERBS.intersection( list(d.keys()) ))
                    if verbs:
                        verb=verbs[0]
                        ll.append( Req(verb,d[verb],d.get("body",None),getHeaders(d),getTests(d),d.get("save",[]),d.get("params",{})) )
                    else:
                        raise RMException("Unknown verb (%s) in '%s'" % (list(d.keys()),fd.name))

            return ll


        list.__init__(self,feed(l) )



###########################################################################
## Helpers
###########################################################################
def listFiles(path,filters=(".yml",".rml") ):
    for folder, subs, files in os.walk(path):
        if folder in [".",".."] or (not os.path.basename(folder).startswith( (".","_"))):
            for filename in files:
                if filename.lower().endswith( filters ):
                    yield os.path.join(folder,filename)


def loadEnv( fd, varenvs=[] ):
    transform.path=None
    if fd:
        if not hasattr(fd,"name"): setattr(fd,"name","")
        try:
            env=yamlLoad( fd ) if fd else {}
            if fd.name:
                print(cw("Using '%s'" % os.path.relpath(fd.name)))
                transform.path = os.path.dirname(fd.name) # change path when executing transform methods, according the path of reqman.conf
        except Exception as e:
            raise RMException("YML syntax in %s\n%s"%(fd.name or "<string>",e))

    else:
        env={}

    for name in varenvs:
        if name not in env:
            raise RMException("the switch '-%s' is unknown ?!" % name)
        else:
            dict_merge(env,env[name] )
    return env

class HtmlRender(list):
    def __init__(self):
        list.__init__(self,["""
<meta charset="utf-8">
<style>
body {font-family: sans-serif;font-size:90%}
.ok {color:green}
.ko {color:red}
hr {padding:0px;margin:0px;height: 1px;border: 0;color: #CCC;background-color: #CCC;}
pre {padding:4px;border:1px solid black;background:white !important;overflow-x:auto;width:100%;max-height:300px;margin:2px;}
span.title {cursor:pointer;}
span.title:hover {background:#EEE;}
i {float:right;color:#AAA}
i.bad {color:orange}
i.good {color:green}
ol,ul {margin:0px;}
ol {padding:0px;}
ol > li {background:#FFE;border-bottom:1px dotted grey;padding:4px;margin-left:16px}
li.hide {background:inherit}
li.hide > ul > span {display:none}
h3 {color:blue;margin:8 0 0 0;padding:0px}
.info {position:fixed;top:0px;right:0px;background:rgba(1,1,1,0.2);border-radius:4px;text-align:right;padding:4px}
.info > * {display:block}
</style>
"""])

    def add(self,html=None,tr=None):
        if tr is not None and tr.req and tr.res:
            html ="""
<li class="hide">
    <span class="title" onclick="this.parentElement.classList.toggle('hide')" title="Click to show/hide details"><b>%s</b> %s : <b>%s</b> <i>%s</i></span>
    <ul>
        <span>
            <pre title="the request">%s %s<hr/>%s<hr/>%s</pre>
            -> %s
            <pre title="the response">%s<hr/>%s</pre>
        </span>
        %s
    </ul>
</li>
            """ % (
                tr.req.method,
                tr.req.path,
                tr.res.status or tr.res,
                tr.res.time,

                tr.req.method,
                tr.req.url,
                "\n".join(["<b>%s</b>: %s" %(k,v) for k,v in list(tr.req.headers.items())]),
                cgi.escape( prettify( str(tr.req.body or "") ) ),

                tr.res.status or "",

                "\n".join(["<b>%s</b>: %s" %(k,v) for k,v in list(tr.res.headers.items())]),
                cgi.escape( prettify( str(tr.res.content or "")) ),

                "".join(["<li class='%s'>%s</li>" % (t and "ok" or "ko",cgi.escape(t.name)) for t in tr ]),
                )
        if html: self.append( html )

    def save(self,name):
        with open(name,"w+") as fid:
            fid.write( os.linesep.join(self) )


def findRCUp(fromHere):
    """Find the rc in upwards folders"""
    current = os.path.realpath(fromHere)
    while 1:
        rc=os.path.join( current,REQMAN_CONF )
        if os.path.isfile(rc): break
        next = os.path.realpath(os.path.join(current,".."))
        if next == current:
            rc=None
            break
        else:
            current=next
    return rc

def resolver(params):
    """ return tuple (reqman.conf,ymls) finded with params """
    ymls=[]
    paths=[]

    for p in params:
        if os.path.isdir(p):
            ymls+=sorted(list(listFiles(p)), key=lambda x: x.lower())
            paths+=[os.path.dirname(i) for i in ymls]
        elif os.path.isfile(p):
            paths.append( os.path.dirname(p) )
            ymls.append(p)
        else:
            raise RMException("bad param: %s" % p) #TODO: better here

    # choose first reqman.conf under choosen files
    rc=None
    folders=list(set(paths))
    folders.sort( key=lambda i: i.count("/")+i.count("\\"))
    for f in folders:
        if os.path.isfile( os.path.join(f,REQMAN_CONF) ):
            rc=os.path.join(f,REQMAN_CONF)

    #if not, take the first reqman.conf in backwards
    if rc is None:
        rc=findRCUp(folders[0] if folders else ".")

    ymls.sort( key = lambda x: x.lower() )
    return rc,ymls

def makeReqs(reqs,env):
    if reqs:
        if env and ("BEGIN" in env):
            r=io.StringIO("call: BEGIN")
            r.name="BEGIN (%s)" % REQMAN_CONF
            reqs = [ Reqs(r,env) ] + reqs

        if env and ("END" in env):
            r=io.StringIO("call: END")
            r.name="END (%s)" % REQMAN_CONF
            reqs = reqs + [ Reqs(r,env) ]

    return reqs

def create(url):
    """ return a (reqman.conf, yml_file) based on the test 'url' """
    hp=urllib.parse.urlparse( url )
    if hp and hp.scheme and hp.hostname:
        root="%s://%s" % (hp.scheme,hp.hostname) + (hp.port and ":%s"%hp.port or "")
        rc=u"""
root: %(root)s
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
""" % locals()
    else:
        root=""
        rc=None

    path= hp.path + ("?"+hp.query if hp.query else "")

    yml=u"""# test created for "%(root)s%(path)s" !

- GET: %(path)s
#- GET: %(root)s%(path)s
  tests:
    - status: 200
""" % locals()
    return rc,yml

def main(params=[]):
    try:
        if len(params)==2 and params[0].lower()=="new":
            ## CREATE USAGE
            rc=findRCUp(".")
            if rc:
                print(cw("Using '%s'" % os.path.relpath(rc)))

            conf,yml=create(params[1])
            if conf:
                if not rc:
                    print("Create",REQMAN_CONF)
                    with open(REQMAN_CONF,"w") as fid: fid.write(conf)
            else:
                if not rc:
                    raise RMException("there is no '%s', you shoul provide a full url !" % REQMAN_CONF)

            ff=glob.glob("*_test.rml")
            yname = "%04d_test.rml" % ((len(ff)+1)*10)

            print("Create",yname)
            with open(yname,"w") as fid: fid.write(yml)

            return 0

        # search for a specific env var (starting with "-")
        switchs=[]
        for switch in [i for i in params if i.startswith("-")]:
            params.remove( switch )
            switchs.append( switch[1:] )

        if "-ko" in switchs:
            switchs.remove("-ko")
            onlyFailedTests=True
        else:
            onlyFailedTests=False

        rc,ymls=resolver(params)

        # load env !
        if rc:
            with open(rc,"r") as fid:
                env=loadEnv( fid, switchs )
        else:
            env=loadEnv( None, switchs )

        fn="reqman.html"

        ll=[]
        for i in ymls:
            with open(i,"r") as fid:
                ll.append( Reqs(fid,env) )

        reqs=makeReqs(ll,env)

        if reqs:
            # and make tests
            alltr=[]
            hr=HtmlRender()
            for f in reqs:
                print()
                print("TESTS:",cb(f.name))
                times=[]
                trs=[]
                for t in f:
                    tr=t.test( env ) #TODO: colorful output !
                    if tr.res: times.append( tr.res.time )
                    if onlyFailedTests:
                        if not all(tr):
                            print( tr )
                    else:
                        print( tr )
                    trs.append( tr)
                    alltr+=tr
                # html rendering...
                avg = sum(times,datetime.timedelta())/len(times) if len(times) else 0
                hr.add("<h3>%s</h3>"%f.name)
                hr.add("<ol>")
                hr.add( "<i style='float:inherit'>%s req(s) avg = %s</i>" % (len(times),avg) )
                for tr in trs:
                    hr.add( tr=tr )
                hr.add("</ol>")



            ok,total=len([i for i in alltr if i]),len(alltr)

            hr.add( "<title>Result: %s/%s</title>" % (ok,total) )
            hr.add( "<div class='info'><span>%s</span><b>%s</b></div>" % ( str(datetime.datetime.now())[:16], " ".join(switchs) ) )

            hr.save( fn )

            if total:
                print()
                print("RESULT: ",(cg if ok==total else cr)("%s/%s" % (ok,total)))
            return total - ok
        else:

            print("""USAGE TEST   : reqman [--opt] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version %s
Test a http service with pre-made scenarios, whose are simple yaml files
(More info on https://github.com/manatlan/reqman)

  <folder|file> : yml scenario or folder of yml scenario
                  (as many as you want)

  [opt]
           --ko : limit standard output to failed tests (ko) only
""" % __version__)

            if env:
                print("""  [switch]      : default to "%s" """ % env.get("root",None) )
                for k,v in env.items():
                    root=v.get("root",None) if type(v)==dict else None
                    if root:
                        print("""%15s : "%s" """ % ("-"+k,root))
            else:
                print("""  [switch]      : pre-made 'switch' defined in a %s""" % REQMAN_CONF)


            return -1

    except RMException as e:
        print()
        print("ERROR: %s" % e)
        return -1
    except KeyboardInterrupt as e:
        print()
        print("ERROR: process interrupted")
        return -1

if __name__=="__main__":
    sys.exit( main(sys.argv[1:]) )
    #~ exec(open("tests.py").read())
