#!/usr/bin/python
# -*- coding: utf-8 -*-
# #
# #    Copyright (C) 2018 manatlan manatlan[at]gmail(dot)com
# #
# # This program is free software; you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published
# # by the Free Software Foundation; version 2 only.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #

import yaml,os,json,sys,httplib,urllib,ssl,sys,fnmatch,urlparse,glob

class SyntaxException(Exception):pass
###########################################################################
## http access
###########################################################################
class Request:
    def __init__(self,protocol,host,port,method,path,data=None,headers={}):
        self.protocol=protocol
        self.host=host
        self.port=port
        self.method=method
        self.path=path
        self.data=data
        self.headers=headers
    def __repr__(self):
        return "[%s %s %s]" % (self.protocol.upper(),self.method,self.path)

class Response:
    def __init__(self,r):
        self.status = r.status
        self.content = r.read()
        self.headers = dict(r.getheaders())
    def __repr__(self):
        return "[%s]" % (self.status)
        #~ return "[%s %s]" % (self.status,self.headers)
        #~ return "<%s %s : %s>" % (self.status,self.headers,self.content.encode("string_escape"))

def http(r):
    if r.protocol=="https":
        cnx=httplib.HTTPSConnection(r.host,r.port,context=ssl._create_unverified_context())
    else:
        cnx=httplib.HTTPConnection(r.host,r.port)
    cnx.request(r.method,r.path,r.data,r.headers)
    return Response(cnx.getresponse())

###########################################################################
## Reqs manage
###########################################################################
class TestResult(list):
    def __init__(self,req,res,tests):
        self.req=req
        self.res=res
        results=[]
        for test in tests:
            what,value = test.keys()[0],test.values()[0]

            testname = "%s = %s" % (what,value)
            if what=="status":  result = int(value)==int(self.res.status)
            elif what=="content": result = value in self.res.content
            else: result = value in self.res.headers.get(what,"")

            results.append( (testname,result) )

        list.__init__(self,results)

    def __repr__(self):
        print " -",self.req,"--->",self.res
        for testname,result in self:
            print "   - TEST:",testname,"?",result
        return ""

class Req(object):
    def __init__(self,method,path,body=None,headers={},tests=[]):  # body = str ou dict ou None
        if body and not isinstance(body,basestring): body=json.dumps(body)

        self.method=method.upper()
        self.path=path
        self.body=body
        self.headers=headers
        self.tests=tests

    def test(self,env=None):

        def rep(txt):
            if env and txt:
                for key,value in env.items():
                    if isinstance(value,basestring):
                        txt=txt.replace("{{%s}}"%key, value.encode('string_escape') )
            return txt

        if env and "root" in env:
            h=urlparse.urlparse( env["root"] )
        else:
            h=urlparse.urlparse( self.path )

        headers=env.get("headers",{}).copy() if env else {}
        headers.update(self.headers)
        for k in headers:
            headers[k]=rep(headers[k])

        req=Request(h.scheme,h.hostname,h.port,self.method,rep(self.path),rep(self.body),headers)
        res=http( req )

        return TestResult(req,res,self.tests)


    def __repr__(self):
        return "<%s %s>" % (self.method,self.path)

class Reqs(list):
    def __init__(self,fd):
        self.name = fd.name.replace("\\","/")
        l=yaml.load( fd.read() )
        ll=[]
        if l:
            l=[l] if type(l)==dict else l

            for d in l:
                if "GET" in d: method,path="GET",d.get("GET","")
                elif "PUT" in d: method,path="PUT",d.get("PUT","")
                elif "POST" in d: method,path="POST",d.get("POST","")
                elif "DELETE" in d: method,path="DELETE",d.get("DELETE","")
                else: raise SyntaxException("no known verbs")
                ll.append( Req(method,path,d.get("body",None),d.get("headers",[]),d.get("tests",[])) )
        list.__init__(self,ll)

def makeTests(env,match="*"):
    ll=[Reqs(file(i)) for i in fnmatch.filter( sorted(glob.glob("*.yml")+glob.glob("*/*.yml")+glob.glob("*/*/*.yml")), match) ]
    for f in ll:
        print f.name,len(f)

        for t in f:
            print t.test( env )

###########################################################################
## Environnements
###########################################################################
def loadEnv(name=None):
    env=yaml.load( file("reqman.conf").read() ) if os.path.isfile("reqman.conf") else {}
    if name in env: env.update( env[name] )
    if "oauth2" in env:
        u = urlparse.urlparse(env["oauth2"]["url"])
        req=Request(u.scheme,u.hostname,u.port,"POST",u.path,urllib.urlencode(env["oauth2"]["params"]),{'Content-Type': 'application/x-www-form-urlencoded'})
        res=http(req)
        token=json.loads(res.content)
        env["headers"]["Authorization"] = token["token_type"]+" "+token["access_token"]
        print "OAuth2 TOKEN:",env["headers"]["Authorization"]
    return env

if __name__=="__main__":
    os.chdir(os.path.join(os.path.dirname(__file__),"."))
    
    #~ makeTests( loadEnv("ROA") )
    #~ makeTests( loadEnv("GATEWAY") )
    makeTests( loadEnv(),"*nas*" )
