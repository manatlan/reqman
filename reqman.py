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
import yaml         # see "pip install pyaml"
import os,json,sys,httplib,urllib,ssl,sys,urlparse,glob,cgi,socket,re,copy,collections,xml.dom.minidom,Cookie,cookielib,urllib2,mimetools,StringIO,datetime


class NotFound: pass
class RMException(Exception):pass

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

def u(txt):
    """ decode txt to unicode """
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


def ub(txt):
    """ same as u, but assume if decode trouble -> it's binary, and so return
        a string that represents the BINARY STUFF, to be able to display it
    """
    try:
        return u(txt)
    except:
        return "*** BINARY SIZE(%s) ***" % len(txt) #TODO: not great for non-response body

def dict_merge(dct, merge_dct):
    """ merge 'merge_dct' in --> dct """
    for k, v in merge_dct.iteritems():
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
                    return len(elem.keys())
                else:
                    elem= elem.get(i,NotFound)
        except (ValueError,IndexError) as e:
            return NotFound
    return elem



###########################################################################
## http request/response
###########################################################################

class CookieStore(cookielib.CookieJar):
    """ Manage cookiejar for httplib-like """
    def saveCookie(self,headers,url):
        if type(headers)==dict: headers=headers.items()
        class FakeResponse:
            def __init__(self, headers=[]):
                """headers: list of RFC822-style 'Key: value' strings"""
                self._headers = mimetools.Message(StringIO.StringIO("\n".join(headers)))
            def info(self): return self._headers
        response = FakeResponse( [ ": ".join([k,v]) for k,v in headers] )
        self.extract_cookies(response, urllib2.Request(url) )

    def getCookieHeaderForUrl(self,url):
        r=urllib2.Request(url)
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

        self.url="%s://%s%s" % (
            self.protocol,
            (self.host or "")+(":%s"%self.port if self.port else ""),
            self.path
        )

        self.headers = COOKIEJAR.getCookieHeaderForUrl( self.url )

        self.headers.update(headers)


    def __repr__(self):
        return cy(self.method)+" "+self.path


class Response:
    def __init__(self,status,body,headers,url):
        self.status = status
        self.content = ub(body)
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


def http(r):
    try:
        if r.protocol and r.protocol.lower()=="https":
            cnx=httplib.HTTPSConnection(r.host,r.port,context=ssl._create_unverified_context()) #TODO: ability to setup a verified ssl context ?
        else:
            cnx=httplib.HTTPConnection(r.host,r.port)
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
    except httplib.BadStatusLine:
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
        results=[]
        for test in tests:
            what,value = test.keys()[0],test.values()[0]

            val = "null" if value is None else "true" if value is True else "false" if value is False else value

            testname = "%s = %s" % (what,val)
            testnameKO = "%s != %s" % (what,val)
            if what=="status":  result = int(value)==(self.res.status and int(self.res.status))
            elif what=="content": result = value in self.res.content
            elif what.startswith("json."):
                try:
                    jzon=json.loads(self.res.content)
                    val=jpath(jzon,what[5:])
                    val=None if val == NotFound else val

                    result = (value == val)
                except:
                    result=False
            else: result = (value in self.res.headers.get(what,""))
            #TODO: test if header is just present

            results.append( Test(result,testname,testnameKO) )

        list.__init__(self,results)

    def __str__(self):
        ll=[""]
        ll.append( cy("*")+u" %s --> %s " % (self.req,cw(str(self.res)) if self.res else cr(u"Not callable") ) )
        for t in self:
            ll.append( u"  - %s: %s" % ( cg("OK") if t==1 else cr("KO"),t.name ) )
        txt = os.linesep.join(ll)
        return txt.encode( sys.stdout.encoding if sys.stdout.encoding else "utf8")

def getVar(env,var):
    if var in env:
        return env[var]
    elif "|" in var:
        key,method=var.split("|",1)

        if key in env:
            content = env[key]
            for m in method.split("|"):
                content=transform(content,env,m)
            return content
        else:
            raise RMException("Can't resolve "+key+" in : "+ ", ".join(env.keys()))

    elif "." in var:
        val=jpath(env,var)
        if val is NotFound:
            raise RMException("Can't resolve "+var+" in : "+ ", ".join(env.keys()))
        return val
    else:
        raise RMException("Can't resolve "+var+" in : "+ ", ".join(env.keys()))



def transform(content,env,methodName):
    if content and methodName:
        if methodName in env:
            code=getVar(env,methodName)
            try:
                exec "def DYNAMIC(x):\n" + ("\n".join(["  "+i for i in code.splitlines()])) in globals()
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
                content=DYNAMIC( x )
            except Exception as e:
                raise RMException("Error in execution of method "+methodName+" : "+str(e))
            finally:
                if transform.path:
                    os.chdir(curdir)
        else:
            raise RMException("Can't find method "+methodName+" in : "+ ", ".join(env.keys()))
    return content

transform.path=None # change cd cwd for transform methods when executed

class Req(object):
    def __init__(self,method,path,body=None,headers={},tests=[],save=None,params={}):  # body = str ou dict ou None
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

        def rep(txt,escapeString=False):
            if cenv and txt and isinstance(txt,basestring):
                for vvar in re.findall("\{\{[^\}]+\}\}",txt)+re.findall("<<[^>]+>>",txt):
                    var=vvar[2:-2]

                    try:
                        val=rep(getVar(cenv,var))   #recursive here ! (if myvar="{{otherVar}}"", redo a pass to resolve otherVar)
                    except RuntimeError:
                        raise RMException("Recursion trouble for '%s'" % var)
                    #val=getVar(cenv,var)
                    if val is NotFound:
                        raise RMException("Can't resolve "+var+" in : "+ ", ".join(cenv.keys()))
                    else:
                        if val is None:
                            val=""
                        elif val is True:
                            val="true"
                        elif val is False:
                            val="false"
                        elif isinstance(val,basestring):
                            if type(val)==unicode: val=val.encode("utf8")   #TODO: do better here
                        elif type(val) in [list,dict]:
                            val=json.dumps(val)
                        else: #int, float, ...
                            val=json.dumps(val)

                        if escapeString:
                            txt=txt.replace( vvar , val.encode("string_escape") )
                        else:
                            txt=txt.replace( vvar , val )

            return txt

        # path ...
        path = rep(self.path)
        if cenv and (not path.strip().lower().startswith("http")) and ("root" in cenv):
            h=urlparse.urlparse( cenv["root"] )
            if h.path and h.path[-1]=="/":
                if path[0]=="/":
                    path=h.path + path[1:]
                else:
                    path=h.path + path
            else:
                path=h.path + path
        else:
            h=urlparse.urlparse( path )
            path = h.path + ("?"+h.query if h.query else "")

        # headers ...
        headers=cenv.get("headers",{}).copy() if cenv else {}
        try:
            headers.update(self.headers)                        # override with self headers
        except ValueError:
            raise RMException("'headers:' should be filled of key/value pairs (ex: 'Content-Type: text/plain')")

        headers={ k:rep(v) for k,v in headers.items() if v is not None}

        # body ...
        if self.body and not isinstance(self.body,basestring):

            def jrep(x): # "json rep"
                r=rep(x)
                if r and isinstance(r,basestring):
                    try:
                        return json.loads(r)
                    except ValueError:
                        return r
                else:
                    return r

            #================================
            def apply(body,method):
                if type(body)==list:
                    return [ apply(i,method) for i in body]
                elif type(body)==dict:
                    return { k:apply(v,method) for k,v in body.items() }
                else:
                    return method(body)
            #================================

            body=apply(self.body, jrep )
            body=json.dumps( body ) # and convert to string !
        else:
            body=rep(self.body,True) #body is a string, so we should ensure escaping string in string !

        req=Request(h.scheme,h.hostname,h.port,self.method,path,body,headers)
        if h.hostname:

            tests=[]+cenv.get("tests",[]) if cenv else []
            tests+=self.tests                               # override with self tests

            try:
                tests=[{test.keys()[0]:rep(test.values()[0])} for test in tests]    # replace vars
            except AttributeError:
                raise RMException("'tests:' should be a list of mono key/value pairs (ex: '- status: 200')")

            timeout=cenv.get("timeout",None)
            try:
                socket.setdefaulttimeout( timeout and float(timeout)/1000.0 )
            except ValueError:
                socket.setdefaulttimeout( None )

            res=http( req )
            if self.save and isinstance(res,Response):
                try:
                    env[ self.save ]=json.loads(res.content)
                except:
                    env[ self.save ]=res.content

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
            l=yaml.load( u(fd.read()) )
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
                    if "call" in d.keys():
                        callname = d["call"]
                        del d["call"]

                        commands = procedures[callname] if callname in procedures else self.env[callname] if callname in self.env else None # local proc in first !

                        if commands:
                            commands=[commands] if type(commands)==dict else commands # ensure we've got a list

                            ncommands=[]
                            for command in commands:
                                q = copy.deepcopy( command )
                                dict_merge(q,d)
                                ncommands.append( q )

                            ll+= feed(ncommands)    # *recursive*

                            continue
                        else:
                            raise RMException("call a not defined procedure '%s' in '%s'" % (callname,fd.name))
                    elif len(d.keys())==1: # a declaration of a procedure ?
                        callname=d.keys()[0]
                        if type(d[callname]) in [dict,list]:    # dict is one call, list is a list of dict (multiple calls) -> so it's a procedure
                            procedures[callname] = d[callname]        # save it
                            continue  # just declare and nothing yet
                        else:
                            # it's, perhaps, a single command (ex: "- GET: /")
                            pass

                    verbs=list(KNOWNVERBS.intersection( d.keys() ))
                    if verbs:
                        verb=verbs[0]
                        ll.append( Req(verb,d[verb],d.get("body",None),d.get("headers",[]),d.get("tests",[]),d.get("save",None),d.get("params",{})) )
                    else:
                        raise RMException("Unknown verbs (%s) in '%s'" % (d.keys(),fd.name))

            return ll


        list.__init__(self,feed(l) )



###########################################################################
## Helpers
###########################################################################
def listFiles(path,filters=(".yml",".rml") ):
    for folder, subs, files in os.walk(path):
        for filename in files:
            if filename.lower().endswith( filters ):
                yield os.path.join(folder,filename)


def loadEnv( fd, varenvs=[] ):
    if fd:
        if not hasattr(fd,"name"): setattr(fd,"name","")
        try:
            env=yaml.load( u(fd.read()) ) if fd else {}
            if fd.name:
                print cw("Use '%s'" % fd.name)
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
.info {position:fixed;top:0px;right:0px;background:rgba(1,1,1,0.2);border-radius:4px;text-align:right}
.info > * {display:block}
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
                tr.res.status or tr.res,

                tr.req.method,
                tr.req.url,
                u"\n".join([u"<b>%s</b>: %s" %(k,v) for k,v in tr.req.headers.items()]),
                cgi.escape( prettify( u(tr.req.body or "")) ),

                u"\n".join([u"<b>%s</b>: %s" %(k,v) for k,v in tr.res.headers.items()]),
                cgi.escape( prettify( u(tr.res.content or "")) ),

                u"".join([u"<li class='%s'>%s</li>" % (t and u"ok" or u"ko",cgi.escape(t.name)) for t in tr ]),
                )
        if html: self.append( html )

    def save(self,name):
        open(name,"w+").write( os.linesep.join(self).encode("utf8") )

def resolver(params):
    """ return tuple (reqman.conf,ymls) finded with params """
    # sort params as yml files
    if not params: params=["."]

    ymls=[]
    paths=[]

    for p in params:
        if os.path.isdir(p):
            ymls+=sorted(list(listFiles(p)), key=lambda x: x.lower())
            paths+=[os.path.dirname(i) for i in ymls]
        elif os.path.isfile(p):
            paths.append( os.path.dirname(p) )
            if p.lower().endswith(".yml") or p.lower().endswith(".rml"):
                ymls.append(p)
            else:
                raise RMException("not a rml file") #TODO: better here
        else:
            raise RMException("bad param: %s" % p) #TODO: better here


    # choose first reqman.conf under choosen files
    rc=None
    folders=list(set(paths))
    folders.sort( key=lambda i: i.count("/")+i.count("\\"))
    for f in folders:
        if os.path.isfile( os.path.join(f,"reqman.conf") ):
            rc=os.path.join(f,"reqman.conf")

    #if not, take the first reqman.conf in backwards
    if rc is None and folders:
        current = os.path.realpath(folders[0])
        while 1:
            rc=os.path.join( current,"reqman.conf" )
            if os.path.isfile(rc): break
            next = os.path.realpath(os.path.join(current,".."))
            if next == current:
                rc=None
                break
            else:
                current=next

    ymls.sort( key = lambda x: x.lower() )
    return rc,ymls

def makeReqs(reqs,env):
    if env and ("BEGIN" in env):
        r=StringIO.StringIO("call: BEGIN")
        r.name="BEGIN (reqman.conf)"
        reqs = [ Reqs(r,env) ] + reqs

    if env and ("END" in env):
        r=StringIO.StringIO("call: END")
        r.name="END (reqman.conf)"
        reqs = reqs + [ Reqs(r,env) ]

    return reqs

def main(params):
    try:
        # search for a specific env var (starting with "-")
        varenvs=[]
        for varenv in [i for i in params if i.startswith("-")]:
            params.remove( varenv )
            varenvs.append( varenv[1:] )

        rc,ymls=resolver(params)

        # load env !
        env=loadEnv( file(rc) if rc else None, varenvs )

        fn="reqman.html"


        reqs=makeReqs([Reqs(file(i),env) for i in ymls],env)

        if reqs:
            # and make tests
            all=[]
            hr=HtmlRender()
            for f in reqs:
                print
                print "TESTS:",cb(f.name)
                hr.add("<h3>%s</h3>"%f.name)
                for t in f:
                    tr=t.test( env ) #TODO: colorful output !
                    print tr
                    hr.add( tr=tr )
                    all+=tr

            ok,total=len([i for i in all if i]),len(all)

            hr.add( "<title>Result: %s/%s</title>" % (ok,total) )
            hr.add( "<div class='info'><i>%s</i><b>%s</b></div>" % ( str(datetime.datetime.now())[:16], " ".join(varenvs) ) )

            hr.save( fn )

            print
            print "RESULT: ",(cg if ok==total else cr)("%s/%s" % (ok,total))
            return total - ok
        else:
            print "ERROR: No tests found !"
            return -1

    except RMException as e:
        print
        print "ERROR: %s" % e
        return -1
    except KeyboardInterrupt as e:
        print
        print "ERROR: process interrupted"
        return -1

if __name__=="__main__":
    sys.exit( main(sys.argv[1:]) )
    #~ execfile("tests.py")
