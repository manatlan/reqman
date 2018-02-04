#!/usr/bin/python
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
import yaml,os,json,sys,httplib,urllib,ssl,sys,urlparse,glob,cgi,socket,re

def u(txt):
    if txt and isinstance(txt,basestring):
        if type(txt) != unicode:
            try:
                return txt.decode("utf8")
            except:
                try:
                    return txt.decode("cp1252")
                except:
                    return unicode(txt)
    return txt


class SyntaxException(Exception):pass
class ErrorException(Exception):pass
###########################################################################
## http request/response
###########################################################################
COOKIEJAR=None

class Request:
    def __init__(self,protocol,host,port,method,path,body=None,headers={}):
        global COOKIEJAR
        self.protocol=protocol
        self.host=host
        self.port=port
        self.method=method
        self.path=path
        self.body=body
        self.headers=headers
        if COOKIEJAR:
            self.headers["cookie"]=COOKIEJAR

        if self.host and self.protocol:
            self.url="%s://%s%s" % (
                self.protocol,
                self.host+(":%s"%self.port if self.port else ""),
                self.path
            )

    def __repr__(self):
        return "[%s %s %s]" % (self.protocol.upper(),self.method,self.path)

class Response:
    def __init__(self,r):
        global COOKIEJAR
        self.status = r.status
        self.content = u(r.read())      #TODO: bad way to decode to unicode ;-)
        self.headers = dict(r.getheaders())
        if "set-cookie" in self.headers:
            COOKIEJAR = r.getheader('set-cookie') 

    def __repr__(self):
        return "[%s]" % (self.status)


def http(r):
    #TODO: cookies better handling with urllib2 ?!
    try:
        if r.protocol=="https":
            cnx=httplib.HTTPSConnection(r.host,r.port,context=ssl._create_unverified_context()) #TODO: ability to setup a verified ssl context ?
        else:
            cnx=httplib.HTTPConnection(r.host,r.port)
        cnx.request(r.method,r.path,r.body,r.headers)
        return Response(cnx.getresponse())
    except socket.error:
        raise ErrorException("Server is down (%s)?" % ((r.host+":%s" % r.port) if r.port else r.host))

###########################################################################
## Reqs manage
###########################################################################

class Test(int):
    """ a boolean with a name """
    def __new__(cls, name,value):
        s=super(Test, cls).__new__(cls, value)
        s.name = name
        return s

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

            results.append( Test(testname,result) )

        list.__init__(self,results)

    def __str__(self):
        ll=[]
        ll.append( u" - %s --> %s " % (self.req,self.res or u"Not callable" ) )
        for t in self:
            ll.append( u"   - TEST: %s ? %s " %(t.name,t==1) )
        txt = os.linesep.join(ll)
        return txt.encode( sys.stdout.encoding if sys.stdout.encoding else "utf8")

def getVar(env,var):
    if var in env:
        return env[var]
    elif "." in var:
        deb,fin=var.split(".",1)
        return getVar( getVar(env, deb), fin)


class Req(object):
    def __init__(self,method,path,body=None,headers={},tests=[],save=None,params={}):  # body = str ou dict ou None
        if body and not isinstance(body,basestring): body=json.dumps(body)

        self.method=method.upper()
        self.path=path
        self.body=body
        self.headers=headers
        self.tests=tests
        self.save=save
        self.params=params

    def test(self,env=None):

        cenv = env.copy() if env else {}    # current env
        cenv.update( self.params )          # override with self params

        def rep(txt):
            if cenv and txt and isinstance(txt,basestring):
                for vvar in re.findall("\{\{[^\}]+\}\}",txt):
                    var=vvar[2:-2]

                    val=getVar(cenv,var)
                    if val is not None and isinstance(val,basestring):
                        if type(val)==unicode: val=val.encode("utf8")
                        txt=txt.replace( vvar , val.encode('string_escape'))

            return txt


        if cenv and (not self.path.strip().startswith("http")) and ("root" in cenv):
            h=urlparse.urlparse( cenv["root"] )
        else:
            h=urlparse.urlparse( self.path )
            self.path = h.path + ("?"+h.query if h.query else "")

        headers=cenv.get("headers",{}).copy() if cenv else {}
        headers.update(self.headers)                        # override with self headers
        for k in headers:
            headers[k]=rep(headers[k])

        req=Request(h.scheme,h.hostname,h.port,self.method,rep(self.path),rep(self.body),headers)
        if h.hostname:
            res=http( req )
            if self.save:
                try:
                    env[ self.save ]=json.loads(res.content)
                except:
                    env[ self.save ]=res.content

            tests=[]+cenv.get("tests",[]) if cenv else []
            tests+=self.tests                               # override with self tests
            return TestResult(req,res,tests)
        else:
            # no hostname : no response, no tests ! (missing reqman.conf the root var ?)
            return TestResult(req,None,[])

    def __repr__(self):
        return "<%s %s>" % (self.method,self.path)

class Reqs(list):
    def __init__(self,fd):

        defs={}

        self.name = fd.name.replace("\\","/") if hasattr(fd,"name") else "String"
        try:
            l=yaml.load( u(fd.read()) )
        except yaml.parser.ParserError as e:
            raise ErrorException("YML syntax :"+e.problem+" at line "+str(e.context_mark and e.context_mark.line or ""))

        ll=[]
        if l:
            l=[l] if type(l)==dict else l

            for d in l:
                #--------------------------------------------------
                if "def" in d.keys():
                    callname = d["def"]
                    request = d
                    del request["def"]
                    defs[ callname ] = request
                    continue # just declare and nothing yet
                elif "call" in d.keys():
                    callname = d["call"]
                    del d["call"]
                    if callname in defs:
                        override = d.copy()
                        d.update( defs[callname] )
                        d.update( override )
                    else:
                        raise SyntaxException("call a not defined def %s" % callname)
                #--------------------------------------------------
                mapkeys ={ i.upper():i for i in d.keys() }
                verbs= sorted(list(set(mapkeys).intersection(set(["GET","POST","DELETE","PUT","HEAD","OPTIONS","TRACE","PATCH","CONNECT"]))))
                if len(verbs)!=1:
                    raise SyntaxException("no known verbs")
                else:
                    method=verbs[0]
                    ll.append( Req(method,d.get( mapkeys[method],""),d.get("body",None),d.get("headers",[]),d.get("tests",[]),d.get("save",None),d.get("params",{})) )
        list.__init__(self,ll)



###########################################################################
## Helpers
###########################################################################
def listFiles(path,filters=(".yml") ):
    for folder, subs, files in os.walk(path):
        for filename in files:
            if filename.lower().endswith( filters ):
                yield os.path.join(folder,filename)


def loadEnv( fd, varenvs=[] ):
    try:
        env=yaml.load( u(fd.read()) )
    except yaml.parser.ParserError as e:
        raise ErrorException("YML syntax :"+e.problem+" at line "+str(e.context_mark and e.context_mark.line or ""))
    for name in varenvs:
        if name in env:
            conf=env[name].copy()
            for k,v in conf.items():
                if k in env and type(env[k])==dict and type(v)==dict:
                    env[k].update( v )
                elif k in env and type(env[k])==list and type(v)==list:
                    env[k]+= v
                else:
                    env[k]=v
    return env

class HtmlRender(list):
    def __init__(self):
        list.__init__(self,[u"""
<meta charset="utf-8">
<style>
.ok {color:green}
.ko {color:red}
hr {padding:0px;margin:0px;height: 1px;border: 0;color: #CCC;background-color: #CCC;}
pre {padding:4px;border:1px solid black;background:white !important;overflow-x:auto;width:100%;max-height:300px}
div {background:#FFE;border-bottom:1px dotted grey;padding:4px;margin-left:16px}
span {cursor:pointer;}
ul {margin:0px;}
span:hover {background:#EEE;}
div.hide {background:inherit}
div.hide > ul > pre {display:none}
h3 {color:blue;}
</style>
"""])

    def add(self,html=None,tr=None):
        if tr is not None and tr.req and tr.res:
            html =u"""
<div class="hide">
    <span onclick="this.parentElement.classList.toggle('hide')" title="Click to show/hide details"><b>%s</b> %s : <b>%s</b></span>
    <ul>
        <pre title="the request">%s %s<hr/>%s<hr/>%s</pre>
        <pre title="the response">%s<hr/>%s</pre>
        %s
    </ul>
</div>
            """ % (
                tr.req.method,
                tr.req.path,
                tr.res.status,

                tr.req.method,
                tr.req.url,
                u"\n".join([u"<b>%s</b>: %s" %(k,v) for k,v in tr.req.headers.items()]),
                cgi.escape(u(tr.req.body or "")),

                u"\n".join([u"<b>%s</b>: %s" %(k,v) for k,v in tr.res.headers.items()]),
                cgi.escape(u(tr.res.content or "")),

                u"".join([u"<li class='%s'>%s</li>" % (t and u"ok" or u"ko",cgi.escape(t.name)) for t in tr ]),
                )
        if html: self.append( html )

    def save(self,name):
        open(name,"w+").write( os.linesep.join(self).encode("utf8") )

def main(params):
    try:
        # search for a specific env var (starting with "-")
        varenvs=[]
        for varenv in [i for i in params if i.startswith("-")]:
            params.remove( varenv )
            varenvs.append( varenv[1:] )

        # sort params as yml files
        ymls=[]
        if not params: params=["."]
        for p in params:
            if os.path.isdir(p):
                ymls+=sorted(list(listFiles(p)))
            elif os.path.isfile(p):
                if p.lower().endswith(".yml"):
                    ymls.append(p)
                else:
                    raise ErrorException("not a yml file") #TODO: better here
            else:
                raise ErrorException("bad param: %s" % p) #TODO: better here

        # choose first reqman.conf under choosen files
        rc=None
        folders=[""]+list(set([os.path.dirname(i) for i in ymls]))
        folders.sort( key=lambda i: i.count("/"))
        for f in folders:
            if os.path.isfile( os.path.join(f,"reqman.conf") ):
                rc=os.path.join(f,"reqman.conf")

        # load env !
        env=loadEnv( file(rc), varenvs ) if rc else {}

        # hook oauth2
        if "oauth2" in env: #TODO: should found a clever way to setup/update vars in env ! to be better suitable
            up = urlparse.urlparse(env["oauth2"]["url"])
            req=Request(up.scheme,up.hostname,up.port,"POST",up.path,urllib.urlencode(env["oauth2"]["params"]),{'Content-Type': 'application/x-www-form-urlencoded'})
            res=http(req)
            token=json.loads(res.content)
            env["headers"]["Authorization"] = token["token_type"]+" "+token["access_token"]
            print "OAuth2 TOKEN:",env["headers"]["Authorization"]


        # and make tests
        all=[]
        hr=HtmlRender()
        for f in [Reqs(file(i)) for i in ymls]:
            print f.name
            hr.add("<h3>%s</h3>"%f.name)
            for t in f:
                tr=t.test( env ) #TODO: colorful output !
                print tr
                hr.add( tr=tr )
                all+=tr

        ok,total=len([i for i in all if i]),len(all)

        hr.add( "<title>Result: %s/%s</title>" % (ok,total) )
        hr.save("reqman.html")

        print "RESULT: %s/%s" % (ok,total)
        return total - ok
    except ErrorException as e:
        print "ERROR: %s" % e
        return -1

if __name__=="__main__":
    sys.exit( main(sys.argv[1:]) )
