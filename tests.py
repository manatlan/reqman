#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import reqman
import json
import os
import socket
from StringIO import StringIO

fwp = lambda x:x.replace("\\","/") # fake windows path

ONLYs=[]
def only(f):
    ONLYs.append(f.func_name)
    return f

BINARY="".join([chr(i) for i in range(255,0,-1)])

################################################################## mock
def mockHttp(q):
    if q.path=="/test_cookie":
        return reqman.Response( 200, "the content", {"content-type":"text/plain","server":"mock","Set-Cookie":"mycookie=myval"},q.url)
    elif q.path=="/test_binary":
        return reqman.Response( 200, BINARY, {"content-type":"audio/mpeg","server":"mock"},q.url)
    elif q.path=="/test_json":
        my=dict(
            mydict=dict(name="jack"),
            mylist=["aaa",42,dict(name="john")],
        )
        return reqman.Response( 200, json.dumps(my), {"content-type":"application/json","server":"mock"}, q.url)
    elif q.path=="/test_error":
        return reqman.ResponseError( "My Error" )
    else:
        return reqman.Response( 200, "the content", {"content-type":"text/plain","server":"mock"}, q.url)

reqman_http = reqman.http
reqman.http = mockHttp
##################################################################

class Tests_jpath(unittest.TestCase):

    def test_b_aba(self):
        d=reqman.yaml.load("""
        toto:
            val1: 100
            val2: 200
            val3: null

        titi:
            - v1
            - v2:
                a: 1
                b: 2

        whos:
            - pers1:
                name: jo
                age: 42
            - pers2:
                name: jack
                age: 43

        astring: hello
        anumber: 42
        abool: true
        anone: null

        """)
        self.assertEqual( reqman.jpath(d,"tata"), reqman.NotFound )
        self.assertEqual( reqman.jpath(d,"toto.val1"), 100 )
        self.assertEqual( reqman.jpath(d,"toto.val2"), 200 )
        self.assertEqual( reqman.jpath(d,"toto.val3"), None )
        self.assertEqual( reqman.jpath(d,"toto.val4"), reqman.NotFound )
        self.assertEqual( reqman.jpath(d,"toto.0"), reqman.NotFound )
        self.assertEqual( reqman.jpath(d,"toto.1"), reqman.NotFound )
        self.assertEqual( reqman.jpath(d,"toto.2"), reqman.NotFound )
        self.assertEqual( reqman.jpath(d,"toto"), {'val2': 200, 'val1': 100, 'val3':None} )

        self.assertEqual( reqman.jpath(d,"titi") , ['v1', {'v2': {'a': 1, 'b': 2}}] )
        self.assertEqual( reqman.jpath(d,"titi.0") , "v1" )
        self.assertEqual( reqman.jpath(d,"titi.1") , {'v2': {'a': 1, 'b': 2}} )
        self.assertEqual( reqman.jpath(d,"titi.1.v2") , {'a': 1, 'b': 2} )
        self.assertEqual( reqman.jpath(d,"titi.1.v2.b") ,2 )
        self.assertEqual( reqman.jpath(d,"titi.2") , reqman.NotFound )

        self.assertEqual( reqman.jpath(d,"astring") , "hello" )
        self.assertEqual( reqman.jpath(d,"astring.var") , "hello" )
        self.assertEqual( reqman.jpath(d,"astring.0") , "hello" )
        self.assertEqual( reqman.jpath(d,"astring.var.cvx.vcx.fgsd") , "hello" )

        self.assertEqual( reqman.jpath(d,"anumber") , 42 )
        self.assertEqual( reqman.jpath(d,"anumber.var") , 42 )
        self.assertEqual( reqman.jpath(d,"anumber.0") , 42 )
        self.assertEqual( reqman.jpath(d,"anumber.var.cvx.vcx.fgsd") , 42 )

        self.assertEqual( reqman.jpath(d,"abool") , True )
        self.assertEqual( reqman.jpath(d,"abool.var") , True )
        self.assertEqual( reqman.jpath(d,"abool.0") , True )
        self.assertEqual( reqman.jpath(d,"abool.var.cvx.vcx.fgsd") , True )

        self.assertEqual( reqman.jpath(d,"anone") , None )
        self.assertEqual( reqman.jpath(d,"anone.var") , None )
        self.assertEqual( reqman.jpath(d,"anone.0") , None )
        self.assertEqual( reqman.jpath(d,"anone.var.cvx.vcx.fgsd") , None )

        self.assertEqual( reqman.jpath(d,"whos.0.pers1.name") , "jo" )

        # test ".size"
        self.assertEqual( reqman.jpath(d,"whos.size") , 2 )         # 2 items in that list
        self.assertEqual( reqman.jpath(d,"whos.0.size") , 1 )       # one key in that dict
        self.assertEqual( reqman.jpath(d,"whos.0.pers1.size") , 2 ) # 2 keys in this dicts
        self.assertEqual( reqman.jpath(d,"astring.size") , "hello" )    # unknown key for a string return content, see ^
        self.assertEqual( reqman.jpath(d,"anumber.size") , 42 )    # unknown key for a number return content, see ^
        self.assertEqual( reqman.jpath(d,"abool.size") , True )    # unknown key for a bool return content, see ^
        self.assertEqual( reqman.jpath(d,"anone.size") , None )    # unknown key for a null return content, see ^
        self.assertEqual( reqman.jpath(d,"unknown.size") , reqman.NotFound )    # unknown key for a unknown return NotFound, see ^
        self.assertEqual( reqman.jpath(d,".size") , 7 )    # .size at the root --> 7 keys
        self.assertEqual( reqman.jpath(d,"size") , 7 )    # size is assimilatted to .size, so -> 7

class Tests_merge(unittest.TestCase):

    def test_b_aba(self):
        d1={
            "anum": 1,
            "headers": {
                "v1": 1
            },
            "headers1": {
                "v": 0
            },
            "mad": {
                "kif": [
                    "kif1",
                    "kif11"
                ],
                "use": {
                    "v1": 1
                }
            },
            "test1": [
                {
                    "status": 201
                }
            ],
            "tests": [
                {
                    "status": 201
                }
            ]
        }

        d2={
            "anum": 2,
            "headers": {
                "v2": 2
            },
            "headers2": {
                "v": 0
            },
            "mad": {
                "kif": [
                    "kif2",
                    "kif22",
                    "kif222"
                ],
                "use": {
                    "v2": 2
                }
            },
            "test2": [
                {
                    "status": 202
                }
            ],
            "tests": [
                {
                    "status": 202
                }
            ]
        }


        d={}
        reqman.dict_merge(d,d1)
        reqman.dict_merge(d,d2)

        dd={ # print json.dumps( d2, indent=4, sort_keys=True )
            "anum": 2,
            "headers": {
                "v1": 1,
                "v2": 2
            },
            "headers1": {
                "v": 0
            },
            "headers2": {
                "v": 0
            },
            "mad": {
                "kif": [
                    "kif1",
                    "kif11",
                    "kif2",
                    "kif22",
                    "kif222"
                ],
                "use": {
                    "v1": 1,
                    "v2": 2
                }
            },
            "test1": [
                {
                    "status": 201
                }
            ],
            "test2": [
                {
                    "status": 202
                }
            ],
            "tests": [
                {
                    "status": 201
                },
                {
                    "status": 202
                }
            ]
        }

        self.assertEqual( d,dd)


class Tests_colorama(unittest.TestCase):

    def test_b_aba(self):
        self.assertTrue( reqman.cr(None) is None)
        self.assertTrue( "HELLO" in reqman.cy("HELLO"))
        self.assertTrue( "HELLO" in reqman.cr("HELLO"))
        self.assertTrue( "HELLO" in reqman.cg("HELLO"))
        self.assertTrue( "HELLO" in reqman.cb("HELLO"))
        self.assertTrue( "HELLO" in reqman.cw("HELLO"))

class Tests_prettify(unittest.TestCase):

    def test_b_aba(self):
        self.assertEqual( reqman.prettify(None), None )
        self.assertEqual( reqman.prettify("yo"), "yo" )
        self.assertEqual( reqman.prettify("42"), "42" )
        self.assertEqual( reqman.prettify("{not good:json}"), "{not good:json}" )
        self.assertEqual( reqman.prettify('{       "albert":   "jo"   }'), '{\n    "albert": "jo"\n}' )

class Tests_transform(unittest.TestCase):

    def test_b_aba(self):
        env={
            "var": "hello",
            "trans": "return x and x.encode('rot13')",
        }
        self.assertEqual( reqman.transform("xxx",env,"trans"), "kkk" )
        self.assertEqual( reqman.transform(None,env,"trans"), None )
        self.assertRaises(reqman.RMException, lambda: reqman.transform("xxx",env,"trans2") )
        self.assertRaises(reqman.RMException, lambda: reqman.transform(None,env,"trans2") )


class Tests_getVar(unittest.TestCase):

    def test_b_aba(self):
        env={
            "var":"val",
            "var.x":"valx", #this is a var named "var.x" !!
            "mylist":[31,32,33]
        }
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"nib") )
        self.assertEqual( reqman.getVar(env,"var"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )
        self.assertEqual( reqman.getVar(env,"mylist.0"), 31 )
        self.assertEqual( reqman.getVar(env,"mylist.1"), 32 )
        self.assertEqual( reqman.getVar(env,"mylist.2"), 33 )
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"mylist.3") )

    def test_baba_dotted(self):
        env={
            "var":dict( ssvar="val",x="eclipsed" ),
            "var.x":"valx", #this is a var named "var.x" !!
        }
        self.assertEqual( reqman.getVar(env,"var.ssvar"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"var.nimp") )
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"xxx") )


    def test_baba_trans(self):
        env={
            "var": "hello",
            "trans": "return x.encode('rot13')",
        }
        self.assertEqual( reqman.getVar(env,"var"), "hello" )
        self.assertEqual( reqman.getVar(env,"var|trans"), "uryyb" )
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"var|unknown") )

class Tests_CookieStore(unittest.TestCase):
    def test(self):
        import Cookie
        CJ=reqman.CookieStore()

        #------------------------------------------------------ create a cookie using "Cookie"
        c = Cookie.SimpleCookie()
        c["cidf"]="malz"
        c["cidf"]["path"]="/yo"

        c["cidf2"]="malz2"
        headers=[ ("user-Agent","yo"),("content-type","text/html") ]
        for k,v in c.iteritems():
            headers.append(tuple(v.output().split(": ",1)))
        #------------------------------------------------------

        CJ.saveCookie(headers,'http://localhost')
        self.assertEqual( CJ.getCookieHeaderForUrl('http://localhost/yo') , {'Cookie': 'cidf=malz; cidf2=malz2'} )
        self.assertEqual( CJ.getCookieHeaderForUrl('http://localhost/') , {'Cookie': 'cidf2=malz2'} )
        self.assertEqual( CJ.getCookieHeaderForUrl('http://mama.com/') , {} )

        CJ.saveCookie( {"set-cookie":"kkk=va"},'http://mama.com')
        self.assertEqual( CJ.getCookieHeaderForUrl('http://mama.com/') , {'Cookie': 'kkk=va'} )



class Tests_ReqRespCookie(unittest.TestCase):
    def test_1cookie(self):
        reqman.COOKIEJAR.clear()
        res=reqman.Response(200,"ok",{"Set-Cookie":"cook=1"},"http://localhost/")   # set the cookie !

        hr=reqman.Request("http","localhost","80","GET","/",None).headers
        self.assertTrue( "Cookie" in hr )
        self.assertEqual( hr["Cookie"],"cook=1" )
        self.assertFalse( "Cookie" in reqman.Request("http","myhost","80","GET","/",None).headers )

    def test_2cookies(self):
        reqman.COOKIEJAR.clear()
        res=reqman.Response(200,"ok",[ ("Set-Cookie","cook1=1"),("Set-Cookie","cook2=2; Path=/p2")],"http://localhost/")   # set the cookie !

        self.assertEqual( len(reqman.COOKIEJAR), 2)

        hr=reqman.Request("http","localhost","80","GET","/",None).headers
        self.assertTrue( "Cookie" in hr )
        self.assertTrue( "cook1=1" in hr["Cookie"] )
        self.assertFalse( "cook2=2" in hr["Cookie"] )

        hr=reqman.Request("http","localhost","80","GET","/p2",None).headers
        self.assertTrue( "Cookie" in hr )
        self.assertTrue( "cook1=1" in hr["Cookie"] )
        self.assertTrue( "cook2=2" in hr["Cookie"] )

        self.assertFalse( "Cookie" in reqman.Request("http","myhost","80","GET","/",None).headers )

    def test_cookie_override(self):
        reqman.COOKIEJAR.clear()
        res=reqman.Response(200,"ok",{"Set-Cookie":"cook=1"},"http://blahblah.com/")   # set the cookie !

        hr=reqman.Request("http","blahblah.com","80","GET","/",None).headers
        self.assertEqual( hr["Cookie"],"cook=1" )

        res=reqman.Response(200,"ok",{"Set-Cookie":"cook=2"},"http://blahblah.com/")   # set the cookie !
        hr=reqman.Request("http","blahblah.com","80","GET","/",None).headers
        self.assertEqual( hr["Cookie"],"cook=2" )

        self.assertEqual( len(reqman.COOKIEJAR), 1)

class Tests_Req(unittest.TestCase):

    def test_noenv(self):
        r=reqman.Req("get","https://github.com/")
        s=r.test()
        self.assertEqual(s.res.status, 200)

    def test_simplest_env(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/")
        s=r.test(env)
        self.assertEqual(s.res.status, 200)

    def test_simplest_env_with_root_as_url(self):
        env=dict(root="https://github.com/path1")
        r=reqman.Req("Get","/path2")
        self.assertEqual(r.path, "/path2")
        s=r.test(env)
        self.assertEqual(s.req.host, "github.com")
        self.assertEqual(s.req.path, "/path1/path2")
        self.assertEqual(s.req.url, "https://github.com/path1/path2")
        self.assertEqual(s.res.status, 200)


        env=dict(root="https://github.com/path1/")
        r=reqman.Req("Get","/path2")
        self.assertEqual(r.path, "/path2")
        s=r.test(env)
        self.assertEqual(s.req.host, "github.com")
        self.assertEqual(s.req.path, "/path1/path2")
        self.assertEqual(s.req.url, "https://github.com/path1/path2")
        self.assertEqual(s.res.status, 200)


        env=dict(root="https://github.com/path1/")
        r=reqman.Req("Get","path2")
        self.assertEqual(r.path, "path2")
        s=r.test(env)
        self.assertEqual(s.req.host, "github.com")
        self.assertEqual(s.req.path, "/path1/path2")
        self.assertEqual(s.req.url, "https://github.com/path1/path2")
        self.assertEqual(s.res.status, 200)

        ######## without / separator at all
        env=dict(root="https://github.com/path1")

        r=reqman.Req("Get","path2")
        self.assertEqual(r.path, "path2")
        s=r.test(env)
        self.assertEqual(s.req.host, "github.com")
        self.assertEqual(s.req.path, "/path1path2")
        self.assertEqual(s.req.url, "https://github.com/path1path2")
        self.assertEqual(s.res.status, 200)


    def test_simplest_env2(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/toto tata")
        self.assertEqual(r.path, "/toto tata")
        s=r.test(env)
        self.assertEqual(s.req.path, "/toto tata")  #the real call is "/toto%20tata"
        self.assertEqual(s.res.status, 200)



    def test_simplest_env3(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("Get","{{root}}/") # {{root}} it not needed, it's implicit ... but u can, if u want ;-)
        s=r.test(env)
        self.assertEqual(s.res.status, 200)


    def test_http(self):
        env=dict(root="http://github.com/")

        r=reqman.Req("GeT","/")
        s=r.test(env)
        self.assertEqual(s.res.status, 200)

    def test_env_headers_inheritance(self):
        env=dict(root="https://github.com/",headers=dict(h1="my h1"))

        r=reqman.Req("GET","/",headers=dict(h2="my h2"))
        s=r.test(env)
        self.assertEqual("h1" in s.req.headers, True)
        self.assertEqual("h2" in s.req.headers, True)

    def test_env_headers_inheritance_remove(self):
        env=dict(root="https://github.com/",headers=dict(h1="my h1",h2="my h2"))

        r=reqman.Req("GET","/",headers=dict(h1=None))   # remove h1
        s=r.test(env)
        self.assertFalse("h1" in s.req.headers)
        self.assertTrue("h2" in s.req.headers)



    def test_Tests(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("GET","/",tests=[
                    dict(status=200),
                    dict(content="content"),
                    dict(server="mock")
        ])
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual( len(s), 3)
        self.assertTrue( all(s) )

    def test_replace_vars_in_tests(self):
        env=dict(root="https://github.com/",myserver="mock")

        r=reqman.Req("GET","/",tests=[
                    dict(status=200),
                    dict(content="content"),
                    dict(server="{{myserver}}")
        ])
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual( len(s), 3)
        self.assertTrue( all(s) )

    def test_env_var_in_path(self):
        env=dict(root="https://github.com/",a_var="explore")

        r=reqman.Req("GET","/{{a_var}}")
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual("content" in s.res.content, True)

    def test_cookie(self):
        reqman.COOKIEJAR.clear()   # ensure no cookies

        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/test_cookie")  # --> return a cookie header
        s=r.test(env)
        self.assertEqual(s.res.headers["Set-Cookie"], "mycookie=myval")

        c=list(reqman.COOKIEJAR)[0]
        self.assertEqual( c.name, "mycookie" )
        self.assertEqual( c.value, "myval" )

        r=reqman.Req("Get","/")
        s=r.test(env)
        self.assertEqual(s.req.headers["Cookie"], "mycookie=myval") # assert that the cookie persist when sending


    def test_binary(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/test_binary")  # --> return binary
        s=r.test(env)
        self.assertTrue( "*** BINARY" in s.res.content)


    def test_var_float(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var: 0.7823
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/0.7823" )

    def test_var_int(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var: 42
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/42" )

    def test_var_true(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var: true
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/true" )

    def test_var_false(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var: false
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/false" )

    def test_var_None(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var: null
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/" )

    def test_var_list(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var:
        - 13
        - 42
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, "/[13, 42]" )

    def test_var_dict(self):
        f=StringIO("""
- POST: /{{var}}
  params:
    var:
        a: 42
        b: 13
""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, '/{"a": 42, "b": 13}' )

class Tests_Reqs(unittest.TestCase):

    def test_simplest_yml(self):
        f=StringIO("GET: https://github.com/")
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 1)

    def test_encoding_yml(self):
        f=StringIO(u"GET: https://github.com/\nbody: héhé")
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),unicode)

        f=StringIO(u"GET: https://github.com/\nbody: héhé".encode("utf8"))
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),unicode)

        f=StringIO(u"GET: https://github.com/\nbody: héhé".encode("cp1252"))
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),unicode)


    def test_yml(self):
        y="""
- GET : https://github.com/
- PUT: https://github.com/explore
- DELETE  : https://github.com/explore
- POST: https://github.com/explore
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)
        self.assertEqual( [i.method for i in l], ['GET', 'PUT', 'DELETE', 'POST'])

    def test_bad_yml(self):
        f=StringIO("")

        self.assertEqual(reqman.Reqs(f),[])


    def test_bad_yml2(self):
        y="""
- Get: https://github.com/
"""
        f=StringIO(y)
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(f))

    def test_bad_yml3(self):
        y="""
- NOOP: https://github.com/
"""
        f=StringIO(y)

        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(f))

    def test_yml_test_env(self):

        y="""
- GET: /
  headers:
    h2: my h2

- POST: /{{a_var}}
  body: "{{a_var}}"

- PUT: /
  headers:
    h3: "{{a_var}}"
  body:                     # yaml -> json body !
    var: 1
    txt: "{{a_var}}"
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 3)
        get=l[0]
        post=l[1]
        put=l[2]
        self.assertEqual( get.path, "/")
        self.assertEqual( get.body, None)
        self.assertEqual( get.headers, {'h2': 'my h2'})

        self.assertEqual( post.path, "/{{a_var}}")
        self.assertEqual( post.body, "{{a_var}}")
        self.assertEqual( post.headers, [])

        self.assertEqual( put.path, "/")
        self.assertEqual( put.body, {"var": 1, "txt": "{{a_var}}"})
        self.assertEqual( put.headers, {'h3': '{{a_var}}'})

        #=-

        env=dict(
            root="https://github.com/",
            headers=dict(h1="my h1"),
            a_var="explore",
        )

        s=get.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, None)
        self.assertEqual( s.req.path, "/")
        self.assertEqual( s.req.body, None)
        self.assertEqual( s.req.headers,  {'h1': 'my h1', 'h2': 'my h2'})

        s=post.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, None)
        self.assertEqual( s.req.path, "/explore")
        self.assertEqual( s.req.body, "explore")
        self.assertEqual( s.req.headers,  {'h1': 'my h1'})

        s=put.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, None)
        self.assertEqual( s.req.path, "/")
        self.assertEqual( json.loads(s.req.body), {"var": 1, "txt": "explore"})
        self.assertEqual( s.req.headers,  {'h1': 'my h1',"h3":"explore"})

    def test_yml_test_env_dotted_var(self):

        y="""
- GET: /{{var}}
- GET: /{{pool.var}}
"""
        f=StringIO(y)

        l=reqman.Reqs(f)
        self.assertEqual( len(l), 2)
        get1=l[0]
        get2=l[1]

        self.assertEqual( get1.path, "/{{var}}")
        self.assertEqual( get2.path, "/{{pool.var}}")

        env=dict(
            root="https://github.com/",
            var="val",
            pool=dict(var="val_from_pool")
        )

        tr=get1.test(env)
        self.assertEqual( tr.req.path, "/val")

        tr=get2.test(env)
        self.assertEqual( tr.req.path, "/val_from_pool")

    def test_yml_root_env_override(self):

        y="""
- GET: /explore
- GET: https://github.fr/explore
"""
        f=StringIO(y)
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 2)
        #=-

        env=dict(
            root="https://github.com/",
        )

        ex=lambda x: (x.req.protocol, x.req.host, x.req.path)

        self.assertEqual( ex( l[0].test(env) ), ('https', 'github.com', '/explore') )
        self.assertEqual( ex( l[1].test(env) ), ('https', 'github.fr', '/explore') )


    def test_yml_http_error(self):  # bas status line / server down / timeout

        y="""
- GET: /test_error
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        get=l[0]

        env=dict(
            root="https://github.com:443/",
            tests=[dict(server="mock")],
        )
        s=get.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertTrue( isinstance(s.res, reqman.ResponseError) )


    def test_yml_http_timeout_default(self):
        get=reqman.Reqs(StringIO("""- GET: /"""))[0]

        env=dict(
            root="https://github.com:443/",
            tests=[dict(server="mock")],
        )
        get.test(env)
        self.assertEqual( socket.getdefaulttimeout(), None )


    def test_yml_http_timeout_set(self):
        get=reqman.Reqs(StringIO("""- GET: /"""))[0]
        env=dict(
            root="https://github.com:443/",
            timeout="200",
            tests=[dict(server="mock")],
        )
        get.test(env)
        self.assertEqual( socket.getdefaulttimeout(), 0.2 )

        # and ... timeout is resetted to default
        env=dict(
            root="https://github.com:443/",
            tests=[dict(server="mock")],
        )
        get.test(env)
        self.assertEqual( socket.getdefaulttimeout(), None )


    def test_yml_http_timeout_set_default(self):
        get=reqman.Reqs(StringIO("""- GET: /"""))[0]
        env=dict(
            root="https://github.com:443/",
            timeout=None,
            tests=[dict(server="mock")],
        )
        get.test(env)
        self.assertEqual( socket.getdefaulttimeout(), None )

    def test_yml_http_timeout_set_bad(self):
        get=reqman.Reqs(StringIO("""- GET: /"""))[0]
        env=dict(
            root="https://github.com:443/",
            timeout="DHSJHDHSSFSDFFD",
            tests=[dict(server="mock")],
        )
        get.test(env)
        self.assertEqual( socket.getdefaulttimeout(), None )



    def test_yml_tests_inheritance(self):

        y="""
- GET: /
  tests:
    - content-type: text/plain
"""
        f=StringIO(y)
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 1)
        get=l[0]
        self.assertEqual( get.path, "/")
        self.assertEqual( get.body, None)
        self.assertEqual( get.tests, [{'content-type': 'text/plain'}])
        #=-

        env=dict(
            root="https://github.com:443/",
            tests=[dict(server="mock")],
        )

        s=get.test(env)
        self.assertTrue( "-->" in str(s))   #TODO: not super ;-)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, 443)
        self.assertEqual( s.req.path, "/")
        self.assertEqual( s.req.body, None)
        self.assertEqual( s[0],1 )
        self.assertEqual( s[1],1 )

    def test_yml_tests_json(self):

        y="""
- GET: /test_json
  tests:
    - content-type:         application/json
    - json.mylist.0:        aaa
    - json.mylist.1:        42
    - json.mylist.2.name:   john
    - json.mydict.name:     jack
    - json.mylist.3:        null
    - json.mydict.0:        null
    - json.0:               null

"""
        f=StringIO(y)
        l=reqman.Reqs(f)

        s=l[0].test( dict(root="https://github.com:443/"))
        self.assertTrue( all(s) )

class Tests_Conf(unittest.TestCase):

    def test_env_override_root(self):
        conf="""
root: AAA
local1:
    root: AA1
local2:
    root: AA2
"""
        e=reqman.loadEnv( StringIO(conf) )
        self.assertEqual( e["root"],"AAA" )

        self.assertRaises(reqman.RMException, lambda: reqman.loadEnv( StringIO(conf), ["unknown"] ) )

        e=reqman.loadEnv( StringIO(conf), ["local1"] )
        self.assertEqual( e["root"],"AA1" )

        e=reqman.loadEnv( StringIO(conf), ["local2"] )
        self.assertEqual( e["root"],"AA2" )

        e=reqman.loadEnv( StringIO(conf), ["local1","local2"] )
        self.assertEqual( e["root"],"AA2" )



    def test_env_override_header_add(self):
        conf="""
headers:
    h1: txt1
    h2: txt2
local:
    headers:
        h3: txt3
"""
        e=reqman.loadEnv( StringIO(conf) )
        self.assertEqual( e["headers"],{'h1': 'txt1','h2': 'txt2'}  )

        e=reqman.loadEnv( StringIO(conf), ["local"] )
        self.assertEqual( e["headers"],{ 'h1':'txt1', 'h2':'txt2', 'h3':'txt3' } )


    def test_env_override_header_replace(self):
        conf="""
headers:
    h1: txt1
    h2: bad
local:
    headers:
        h2: txt2
"""
        e=reqman.loadEnv( StringIO(conf) )
        self.assertEqual( e["headers"],{'h1': 'txt1','h2': 'bad'}  )

        e=reqman.loadEnv( StringIO(conf), ["local"] )
        self.assertEqual( e["headers"],{'h1': 'txt1','h2': 'txt2'} )

    def test_env_override_tests_add(self):
        conf="""
tests:
    - status: 200
local:
    tests:
        - content: yo
"""
        e=reqman.loadEnv( StringIO(conf) )
        self.assertEqual( e["tests"],[{'status': 200}]  )

        e=reqman.loadEnv( StringIO(conf), ["local"] )
        self.assertEqual( e["tests"],[{'status': 200}, {'content': 'yo'}] )



class Tests_Yml_bad(unittest.TestCase):

    def test_conf_exception(self):
        conf="""
i'm a yaml error
fdsq:
"""
        self.assertRaises(reqman.RMException, lambda: reqman.loadEnv( StringIO(conf) ) )


    def test_yml_exception(self):
        f=StringIO("""
i'm a yaml error
fdsq:
""")
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(f) )


    def test_yml_bad_tests(self):
        f=StringIO("""
- GET: http://jim.com
  tests:
      badkey: bad
""")
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(f)[0].test({}) )  #  should be a list of mono key/value pairs (

    def test_yml_bad_headers(self):
        f=StringIO("""
- GET: http://jim.com
  headers:
      - badkey: bad
""")
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(f)[0].test({}) )  #should be a dict


class Tests_env_save(unittest.TestCase):

    def test_create_var(self):
        f=StringIO("""
- GET: http://supersite.fr/rien
  save: newVar
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)

        self.assertEqual( env, {'newVar': u'the content'} )

    def test_create_json_var(self):
        f=StringIO("""
- GET: http://supersite.fr/test_json
  save: newVar
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)

        self.assertEqual( env, {'newVar': {"mylist": ["aaa", 42, {"name": "john"}], "mydict": {"name": "jack"}} } )

    def test_override_var(self):
        f=StringIO("""
- GET: http://supersite.fr/nada
  save: newVar
""")
        l=reqman.Reqs(f)

        env={"newVar":"old value"}
        self.assertEqual( env, {'newVar': u'old value'} )
        l[0].test(env)
        self.assertEqual( env, {'newVar': u'the content'} )

    def test_reuse_var_created(self):
        f=StringIO("""
- GET: http://supersite.fr/rien
  save: var

- POST: http://supersite.fr/rien/yo
  headers:
    Authorizattion: Bearer {{var}}
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)
        self.assertEqual( env, {'var': 'the content'} )

        s=l[1].test(env)
        self.assertEqual( s.req.headers["Authorizattion"], "Bearer the content" )

    def test_bad_reuse_var_created(self):
        f=StringIO("""
- GET: http://supersite.fr/rien
  save: var

- POST: http://supersite.fr/rien/yo
  headers:
    Authorizattion: Bearer {{unknown_var}}
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)
        self.assertEqual( env, {'var': u'the content'} )

        self.assertRaises(reqman.RMException, lambda: l[1].test(env))

    def test_save_var_as_variable(self):
        f=StringIO("""
- justdoit:
    GET: http://supersite.fr/rien
    save: <<my_destination>>

- call: justdoit
  params:
    my_destination: jo
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)
        self.assertEqual( env, {'jo': 'the content'} )


    #~ def test_save_var_to_file_denied(self):  # Works on Windows ;-(
        #~ f=StringIO("""
#~ - GET: http://supersite.fr/rien
  #~ save: file:///at_root
#~ """)
        #~ l=reqman.Reqs(f)

        #~ env={}
        #~ self.assertRaises(reqman.RMException, lambda: l[0].test(env))


    def test_save_var_to_file_txt(self):
        f=StringIO("""
- GET: http://supersite.fr/
  save: file://aeff.txt
""")
        l=reqman.Reqs(f)

        env={}
        self.assertFalse( os.path.isfile("aeff.txt") )
        l[0].test(env)
        self.assertTrue( os.path.isfile("aeff.txt") )
        self.assertEqual( file("aeff.txt").read(), "the content" )

    def test_save_var_to_file_bin(self):
        f=StringIO("""
- GET: http://supersite.fr/test_binary
  save: file://aeff.txt
""")
        l=reqman.Reqs(f)

        env={}
        self.assertFalse( os.path.isfile("aeff.txt") )
        l[0].test(env)
        self.assertTrue( os.path.isfile("aeff.txt") )
        self.assertEqual( open("aeff.txt","rb").read(), BINARY )

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if os.path.isfile("aeff.txt"):
            os.unlink("aeff.txt")



class Tests_procedures_NEW(unittest.TestCase):
    def test_yml_procedures_call_with_diff_types(self):

        y="""
- jo:
      POST: /
      body:
        <<val>>

- call: jo
  params:
    val:
        - 1
        - 2

- call: jo
  params:
    val:
        a: 1
        b: 2

"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 2)

        r=l[0].test({})
        self.assertEqual( json.loads(r.req.body), [1,2] )

        r=l[1].test({})
        self.assertEqual( json.loads(r.req.body), dict(a=1,b=2) )

    def test_yml_procedures_call_with_sub_diff_types(self):

        y="""
- jo:
      POST: /
      body:
        data:
            "{{val}}"

- jack:
      POST: /
      body:
        data:
            <<val>>         # second escaper

- call: jo
  params:
    val:
        - 1
        - 2

- call: jo
  params:
    val:
        a: 1
        b: 2

- call: jack
  params:
    val:
        - 1
        - 2

- call: jack
  params:
    val:
        a: 1
        b: 2

"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)

        r=l[0].test({})
        self.assertEqual( json.loads(r.req.body), {'data': [1, 2]} )

        r=l[1].test({})
        self.assertEqual( json.loads(r.req.body),  {'data': dict(a=1,b=2) } )

        r=l[2].test({})
        self.assertEqual( json.loads(r.req.body), {'data': [1, 2]} )

        r=l[3].test({})
        self.assertEqual( json.loads(r.req.body),  {'data': dict(a=1,b=2) } )


    def test_yml_procedures(self):

        y="""
- jo:
    GET: /
- call: jo
- call: jo
- call: jo
- {"call": "jo"}    #json notation (coz json is a subset of yaml ;-)
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)


    def test_yml_procedures_multiple(self):     # NEW
        y="""
- jo:
    - GET: /
    - POST: /
    - PUT: /
- call: jo
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 3)

        y="""
- jo:
    - GET: /
    - POST: /
    - PUT: /
- call: jo
- call: jo
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 6)



    def test_yml_procedures_multiple_mad(self):     # NEW
        y="""
- jo:
    - jack:
        GET: /

    - call: jack
    - call: jack
- call: jo
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 2)


    def test_yml_procedures_def_without_call(self):

        y="""
- jo:
    GET: /
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 0)    # 0 request !

    def test_yml_procedures_call_without_def(self):

        y="""
- call: me
"""
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(StringIO(y)) )

    def test_yml_procedure_global(self):     # NEW
        y="""
- call: me
"""
        env={
            "me": [{"GET":"/"},{"POST":"/"}],   # declare a global proc
        }

        l=reqman.Reqs(StringIO(y),env)
        self.assertEqual( len(l), 2)








class Tests_params_NEW(unittest.TestCase):

    def test_yml_params(self):

        y="""
- GET: /{{myvar}}
  params:
    myvar: hello
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        env={}
        tr=l[0].test(env)

        self.assertEqual( tr.req.path, "/hello" )

    def test_yml_params_override(self):

        y="""
- GET: /{{myvar}}
  params:
    myvar: this one
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        env={"myvar":"not this"}
        tr=l[0].test(env)

        self.assertEqual( tr.req.path, "/this one" )


    def test_yml_params_override_root(self):

        y="""
- GET: /
  params:
    root: https://this_one.net
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/")

        env={"root":"http://not_this.com"}
        tr=l[0].test(env)
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.host, "this_one.net" )

    def test_yml_params_with_procedures(self):

        y="""
- call_me:
    GET: /{{myvar}}
- call: call_me
  params:
    myvar: bingo
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        tr=l[0].test( dict(root="http://fake.com") )
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bingo" )

    def test_yml_params_with_procedures_override_def_params(self):

        y="""
- call_me:
      GET: /{{myvar}}
      params:
        myvar: bad      # will be overriden
- call: call_me
  params:
    myvar: bingo    # override original defined in def statement
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        tr=l[0].test( dict(root="http://fake.com") )
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bingo" )

    def test_yml_params_with_procedures2(self):

        y="""
- call_me:
      GET: /{{myvar}}
      params:
        myvar: bingo
- call: call_me
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        tr=l[0].test( dict(root="http://fake.com") )
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bingo" )

    def test_yml_params_with_procedures_and_inheritance(self):

        y="""
- METHOD:
      GET: /{{myvar}}/{{myvar2}}
      params:
        myvar2: end
      headers:
        myheader: myheader
      tests:
        - status: 200

- call: METHOD
  params:
    myvar: bingo
  headers:
    myheader2: myheader2
  tests:
    - content-type: text/plain

- call: METHOD
  params:
    myvar: bongi
  headers:
    myheader3: myheader3
  tests:
    - server: mock
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 2)
        self.assertEqual( l[0].path, "/{{myvar}}/{{myvar2}}")
        self.assertEqual( l[1].path, "/{{myvar}}/{{myvar2}}")

        tr=l[0].test( dict(root="http://fake.com") )
        self.assertEqual( len(tr), 2)
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bingo/end" )
        self.assertEqual( tr.req.headers, {'myheader': 'myheader','myheader2': 'myheader2'} )

        tr=l[1].test( dict(root="http://fake.com") )
        self.assertEqual( len(tr), 2)
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bongi/end" )
        self.assertEqual( tr.req.headers, {'myheader': 'myheader','myheader3': 'myheader3'} )

    def test_yml_procedures_with_2params(self):

        y="""
- call_me:
      GET: /{{myvar}}/{{myvar2}}
      params:
        myvar: bingo

- call: call_me
  params:
    myvar2: bongi
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}/{{myvar2}}")

        tr=l[0].test( dict(root="http://fake.com") )
        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bingo/bongi" )

    def test_yml_procedures_with_2params_recursive(self):

        y="""
- call_me:
      GET: /{{myvar}}
      params:
        myvar: "{{my}}"

- call: call_me
  params:
    my: "{{a_val}}"
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        tr=l[0].test( dict(root="http://fake.com",a_val="bongi") )

        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bongi" )


    def test_yml_procedures_with_2params_recursive_secondEscaper(self):

        y="""
- call_me:
      GET: /<<myvar>>
      params:
        myvar: <<my>>

- call: call_me
  params:
    my: <<a_val>>
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/<<myvar>>")

        tr=l[0].test( dict(root="http://fake.com",a_val="bongi") )

        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bongi" )

    def test_yml_procedures_with_params_recursive_horror(self):

        y="""
            - GET: /{{my}}
              params:
                my: "{{my2}}"
                my2: "{{my}}"
        """
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{my}}")

        self.assertRaises(reqman.RMException, lambda: l[0].test({}) )     #reccursion error !!!


    def test_yml_params_escape_string1(self):

        y="""
- POST: /test
  body:
    <<myvar>>
  params:
    myvar: |
        line1
        line2
        line3
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)

        tr=l[0].test({})

        self.assertEqual( tr.req.body, "line1\\nline2\\nline3\\n" )

    def test_yml_params_escape_string2(self):

        y="""
- POST: /test
  body:
    start<<myvar>>end
  params:
    myvar: |
        line1
        line2
        line3
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)

        tr=l[0].test({})

        self.assertEqual( tr.req.body, "startline1\\nline2\\nline3\\nend" )

    def test_yml_params_escape_string3(self):

        y="""
- POST: /test
  body:
    start<<myvar>>end
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)

        tr=l[0].test({"myvar":"aaa\nbbb"})

        self.assertEqual( tr.req.body, "startaaa\\nbbbend" )


    def test_yml_params_escape_string4(self):

        y="""
- proc:
      POST: /test
      body:
        <<myvar>>

- call: proc
  params:
    myvar: |
        start
        <<var>>
        end
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)

        tr=l[0].test({"var":"aaa\nbbb"})

        self.assertEqual( tr.req.body, "start\\naaa\\nbbb\\nend\\n" )

    #~ @only
    def test_yml_prog_embeded_call(self):

        y="""

- proc2:
    - GET: /<<a>>/<<b>>

- proc:
    - call: proc2
      params: {"b":1}
    - call: proc2
      params: {"b":2}

- call: proc
  params: {"a":1}

- call: proc
  params: {"a":2}
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)

        mp=[i.test().req.path for i in l]
        self.assertEqual( mp, ['/1/1', '/1/2', '/2/1', '/2/2'] )

    def test_yml_call_embeded_declaration(self):

        y="""
- proc:
    - proc2:
        - GET: /<<a>>/<<b>>

    - call: proc2
      params: {"b":1}
    - call: proc2
      params: {"b":2}

- call: proc
  params: {"a":1}

- call: proc
  params: {"a":2}
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)

        mp=[i.test().req.path for i in l]
        self.assertEqual( mp, ['/1/1', '/1/2', '/2/1', '/2/2'] )



# ~ class Tests_main(unittest.TestCase):# minimal test ;-( ... to increase % coverage

#     ~ #TODO: test command line more !

#     ~ def test_command_line_bad(self):
#         ~ self.assertEqual(reqman.main(["unknown_param"]),-1)  # bad param
#         ~ self.assertEqual(reqman.main(["examples","-unknown"]),-1)  # unknown switch
#         ~ self.assertEqual(reqman.main(["examples/tests.yml","-unknown"]),-1)  # unknown switch
#         ~ self.assertEqual(reqman.main(["tests.py"]),-1)  # not a yaml file

#     ~ def test_command_line(self):
#         ~ if os.path.isfile("reqman.html"): os.unlink("reqman.html")
#         ~ self.assertEqual(reqman.main(["examples/tests.yml"]),3)  # 2 bad tests
#         ~ self.assertTrue( os.path.isfile("reqman.html") )

# ~ class Tests_real_http(unittest.TestCase):

#     ~ def test_1(self):
#         ~ r=reqman.Request("https","github.com","443","GET","/")
#         ~ self.assertEqual(r.url,"https://github.com:443/")
#         ~ res=reqman_http(r)
#         ~ self.assertEqual(res.status,200)

#     ~ def test_2(self):
#         ~ r=reqman.Request("http","github.com",None,"GET","/")
#         ~ self.assertEqual(r.url,"http://github.com/")
#         ~ res=reqman_http(r)
#         ~ self.assertEqual(res.status,301)

#     ~ def test_3(self):
#         ~ r=reqman.Request("http","localhost",59999,"GET","/")
#         ~ self.assertRaises(reqman.RMException, lambda: reqman_http(r))



class Tests_TRANSFORM(unittest.TestCase):

    def test_trans_var(self):
        env=dict(
            root="https://github.com/",
            trans="return x.encode('rot13')",
        )

        y="""
- GET: /
  body: "{{var|trans}}"
  params:
    var: hello
"""
        l=reqman.Reqs(StringIO(y))
        r=l[0]
        self.assertEqual(r.body,"{{var|trans}}")
        s=r.test(env)
        self.assertEqual(s.req.body,"uryyb")

    def test_trans_chainable(self):
        env=dict(
            root="https://github.com/",
            trans="return x.encode('rot13')",
        )

        y="""
- GET: /
  body: "{{var|trans|trans}}"
  params:
    var: hello
"""
        l=reqman.Reqs(StringIO(y))
        r=l[0]
        self.assertEqual(r.body,"{{var|trans|trans}}")
        s=r.test(env)
        self.assertEqual(s.req.body,"hello")


    def test_call_without_param(self):     # NEW
        y="""
- GET: http://kiki.com/1{{|now}}2
  params:
    now:    return "OK"
"""
        env={}

        l=reqman.Reqs(StringIO(y),env)
        s=l[0].test()
        self.assertEqual( s.req.path, "/1OK2" )

    def test_call_with_value(self):     # NEW
        y="""
- GET: http://kiki.com/{{12|add}}
  params:
    add:    return int(x)+30
"""
        env={}

        l=reqman.Reqs(StringIO(y),env)
        s=l[0].test()
        self.assertEqual( s.req.path, "/42" )


class Tests_resolver_with_rc(unittest.TestCase):

    def setUp(self):
        reqman.os.path.isfile = lambda x: reqman.os.path.realpath(x) in [reqman.os.path.realpath(i) for i in [
            "reqman.conf",
            "jo/f1.yml",
            "jo/f2.yml",
            "jack/f1.yml",
            "jack/f2.yml",
            "jack/reqman.conf",
        ]]

    def tearDown(self):
        reqman.os.path.isfile = os.path.isfile

    def test_fnf(self):
        self.assertRaises(reqman.RMException, lambda: reqman.resolver(["nimp/nimp.yml"]))   # fnf
        self.assertRaises(reqman.RMException, lambda: reqman.resolver(["jo/f1.yml","nimp/nimp.yml"]))   # fnf

        reqman.resolver(["reqman.conf"])

    def test_rc(self):
        rc,ll = reqman.resolver(["jo/f1.yml"])
        self.assertTrue( "reqman.conf" in rc )
        self.assertEquals( len(ll),1 )

    def test_rc2(self):
        rc,ll = reqman.resolver(["jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEquals( len(ll),1 )

class Tests_resolver_without_rc(unittest.TestCase):

    def setUp(self):
        reqman.os.path.isfile = lambda x: reqman.os.path.realpath(x) in [reqman.os.path.realpath(i) for i in [
            "jo/f1.yml",
            "jo/f2.yml",
            "jack/f2.yml",
            "jack/f1.yml",
            "jack/reqman.conf",
            "jim/f1.rml",
            "jim/reqman.conf",
        ]]

    def tearDown(self):
        reqman.os.path.isfile = os.path.isfile

    def test_rc(self):
        rc,ll = reqman.resolver(["jo/f1.yml"])
        self.assertTrue( rc is None )   # no reqman.conf at root !
        self.assertEquals( len(ll),1 )

    def test_rc2(self):
        rc,ll = reqman.resolver(["jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEquals( len(ll),1 )

    def test_rc3(self):
        rc,ll = reqman.resolver(["jo/f1.yml","jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEquals( len(ll),2 )
        self.assertEquals( ll,['jack/f1.yml', 'jo/f1.yml'] )    # sorted

    #~ @only
    def test_rml(self):
        rc,ll = reqman.resolver(["jim/f1.rml"])
        self.assertTrue( "jim/reqman.conf" in fwp(rc) )
        self.assertEquals( len(ll),1 )


class Tests_play(unittest.TestCase):

    def test_call_proc_from_rc(self):

        conf="""
root: https://github.com/
XXX:
    - GET: /start
"""
        env=reqman.loadEnv( StringIO(conf) )

        y="""
- call: XXX
- GET: /
"""
        rs=reqman.Reqs(StringIO(y),env)
        self.assertEqual( len(rs),2)

        ll=reqman.makeReqs([rs],env)
        self.assertEqual( len(ll), 1)


    def test_call_begin_from_rc(self):

        conf="""
root: https://github.com/

BEGIN:
    - GET: /start
"""
        env=reqman.loadEnv( StringIO(conf) )

        y="""
- GET: /
"""
        rs=reqman.Reqs(StringIO(y),env)
        self.assertEqual( len(rs),1)

        ll=reqman.makeReqs([rs],env)
        self.assertEqual( len(ll), 2)

if __name__ == '__main__':

    if ONLYs:
        print "*** WARNING *** skip some tests !"
        def load_tests(loader, tests, pattern):
            suite = unittest.TestSuite()
            for c in tests._tests:
                suite.addTests( [t for t in c._tests if t._testMethodName in ONLYs])
            return suite

    unittest.main( )
