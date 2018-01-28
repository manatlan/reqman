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

import yaml,os,json,sys,httplib,urllib,ssl,sys,urlparse,glob

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
        # return "<%s %s : %s>" % (self.status,self.headers,self.content.encode("string_escape"))

def http(r):
    #TODO: cookiejar !
    #TODO: exception, coz host,port could be none,none if not root and "GET /" for example !
    if r.protocol=="https":
        cnx=httplib.HTTPSConnection(r.host,r.port,context=ssl._create_unverified_context()) #TODO: ability to setup a verified ssl context ?
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
            #TODO: test if header is just present
            #TODO: test if not !

            results.append( (testname,result) ) #TODO: make a (bool)class !

        list.__init__(self,results)

    def __repr__(self): #TODO: should return str
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

        return TestResult(req,res,self.tests) #TODO: inheritance tests !


    def __repr__(self):
        return "<%s %s>" % (self.method,self.path)

class Reqs(list):
    def __init__(self,fd):
        self.name = fd.name.replace("\\","/")
        l=yaml.load( fd.read() )    #TODO: should be aware of encodings (utf8/cp1252 at least) (what for mac ?)
        ll=[]
        if l:
            l=[l] if type(l)==dict else l

            for d in l:
                if "GET" in d: method,path="GET",d.get("GET","")
                elif "PUT" in d: method,path="PUT",d.get("PUT","")
                elif "POST" in d: method,path="POST",d.get("POST","")
                elif "DELETE" in d: method,path="DELETE",d.get("DELETE","")
                #TODO: more http verbs !
                #TODO: no case sensitive verbs !
                else: raise SyntaxException("no known verbs")
                ll.append( Req(method,path,d.get("body",None),d.get("headers",[]),d.get("tests",[])) )
        list.__init__(self,ll)


###########################################################################
## Environnement
###########################################################################
def loadEnv(rc,name=None):
    env=yaml.load( file(rc).read() )
    if name in env: env.update( env[name] ) #TODO: should warn when not present ?!
    if "oauth2" in env: #TODO: should found a clever way to setup/update vars in env ! to be better suitable
        u = urlparse.urlparse(env["oauth2"]["url"])
        req=Request(u.scheme,u.hostname,u.port,"POST",u.path,urllib.urlencode(env["oauth2"]["params"]),{'Content-Type': 'application/x-www-form-urlencoded'})
        res=http(req)
        token=json.loads(res.content)
        env["headers"]["Authorization"] = token["token_type"]+" "+token["access_token"]
        print "OAuth2 TOKEN:",env["headers"]["Authorization"]
    return env

def rlist(path):
    for folder, subs, files in os.walk(path):
        for filename in files:
            if filename.lower().endswith( (".yml") ):
                yield os.path.join(folder,filename)

if __name__=="__main__":
    params=sys.argv[1:]
    # params=["example",]
    if params:

        # search for a specific env var (starting with "-")
        env=[i for i in params if i.startswith("-")]
        assert len(env)<=1  #TODO: better here
        if len(env)==1:
            params.remove(env[0])
            specificEnv=env[0][1:]
        else:
            specificEnv=None
        
        # sort params as yml files
        ymls=[]
        for p in params:
            if os.path.isdir(p):
                ymls+=sorted(list(rlist(params[0])))
            elif os.path.isfile(p):
                if p.lower().endswith(".yml"):
                    ymls.append(p)
                else:
                    raise Exception("not a yml file") #TODO: better here
            else:
                raise Exception("bad param: %s" % p) #TODO: better here

        # choose first reqman.conf under choosen files
        rc=None
        folders=[""]+list(set([os.path.dirname(i) for i in ymls]))
        folders.sort( key=lambda i: i.count("/"))
        for f in folders:
            if os.path.isfile( os.path.join(f,"reqman.conf") ):
                rc=os.path.join(f,"reqman.conf")

        # load env !
        env=loadEnv(rc,specificEnv) if rc else {} 

        # and make tests
        #TODO: make a html renderer too !
        for f in [Reqs(file(i)) for i in ymls]:
            print f.name,len(f)
            for t in f:
                print t.test( env ) #TODO: colorful output !
        #TODO: coolest sys.exit() depending on tests
    else:
        print "USAGE: reqman <pattern> [env]" #TODO: should load all yml under current path, no ?!
        sys.exit(-1)
