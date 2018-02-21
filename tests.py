#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import reqman
import json
import os
from StringIO import StringIO

fwp = lambda x:x.replace("\\","/") # fake windows path

################################################################## mock
def mockHttp(q):
    if q.path=="/test_cookie":
        return reqman.Response( 200, "the content", {"content-type":"text/plain","server":"mock","set-cookie":"mycookie=myval"})
    elif q.path=="/test_binary":
        binary="".join([chr(i) for i in range(255,0,-1)])
        return reqman.Response( 200, binary, {"content-type":"audio/mpeg","server":"mock"})
    elif q.path=="/test_json":
        my=dict(
            mydict=dict(name="jack"),
            mylist=["aaa",42,dict(name="john")],
        )
        return reqman.Response( 200, json.dumps(my), {"content-type":"application/json","server":"mock"})
    else:
        return reqman.Response( 200, "the content", {"content-type":"text/plain","server":"mock"})

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

        self.assertEqual( reqman.jpath(d,"whos.0.pers1.name") , "jo" )

class Tests_colorama(unittest.TestCase):

    def test_b_aba(self):
        self.assertTrue( reqman.cr(None) is None)
        self.assertTrue( "HELLO" in reqman.cy("HELLO"))
        self.assertTrue( "HELLO" in reqman.cr("HELLO"))
        self.assertTrue( "HELLO" in reqman.cg("HELLO"))
        self.assertTrue( "HELLO" in reqman.cb("HELLO"))
        self.assertTrue( "HELLO" in reqman.cw("HELLO"))

class Tests_prettyjson(unittest.TestCase):

    def test_b_aba(self):
        self.assertEqual( reqman.prettyJson(None), None )
        self.assertEqual( reqman.prettyJson("yo"), "yo" )
        self.assertEqual( reqman.prettyJson("42"), "42" )
        self.assertEqual( reqman.prettyJson("{not good:json}"), "{not good:json}" )
        self.assertEqual( reqman.prettyJson('{       "albert":   "jo"   }'), '{\n    "albert": "jo"\n}' )

class Tests_transform(unittest.TestCase):

    def test_b_aba(self):
        env={
            "var": "hello",
            "trans": "return x.encode('rot13')",
        }
        self.assertEqual( reqman.transform("xxx",env,"trans"), "kkk" )
        self.assertEqual( reqman.transform(None,env,"trans"), None )
        self.assertRaises(reqman.RMException, lambda: reqman.transform("xxx",env,"trans2") )
        self.assertEqual( reqman.transform(None,env,"trans2"), None )   # no exception if empty content


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

    def test_simplest_env(self):
        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/toto tata")
        self.assertEqual(r.path, "/toto tata")
        s=r.test(env)
        self.assertEqual(s.req.path, "/toto tata")  #the real call is "/toto%20tata"
        self.assertEqual(s.res.status, 200)



    def test_simplest_env2(self):
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
        reqman.COOKIEJAR=None   # ensure no cookies

        env=dict(root="https://github.com/")

        r=reqman.Req("Get","/test_cookie")  # --> return a cookie header
        s=r.test(env)
        self.assertEqual(s.res.headers["set-cookie"], "mycookie=myval")

        r=reqman.Req("Get","/")
        self.assertFalse("cookie" in r.headers) # the request is virgin
        s=r.test(env)
        self.assertEqual(s.req.headers["cookie"], "mycookie=myval") # assert that the cookie persist when sending

        reqman.COOKIEJAR=None   # ensure no cookies

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
- GEt : https://github.com/
- pUT: https://github.com/explore
- DEleTE  : https://github.com/explore
- post: https://github.com/explore
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)
        self.assertEqual( [i.method for i in l], ['GET', 'PUT', 'DELETE', 'POST'])

    def test_bad_yml(self):
        f=StringIO("")

        self.assertEqual(reqman.Reqs(f),[])

    def test_bad_yml2(self):
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
- POsT: /{{a_var}}
  body: "{{a_var}}"
- PUt: /
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
        #~ print s.res.content
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
        self.assertEqual( env, {'var': u'the content'} )

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




class Tests_macros(unittest.TestCase):

    def test_yml_macros(self):

        y="""
- def: jo
  GET: /
- call: jo
- call: jo
- call: jo
- {"call": "jo"}    #json notation (coz json is a subset of yaml ;-)
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 4)

    def test_yml_macros_def_without_call(self):

        y="""
- def: jo
  GET: /
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 0)    # 0 request !

    def test_yml_macros_call_without_def(self):

        y="""
- call: me
"""
        self.assertRaises(reqman.RMException, lambda: reqman.Reqs(StringIO(y)) )



class Tests_params(unittest.TestCase):

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

    def test_yml_params_with_macros(self):

        y="""
- def: call_me
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

    def test_yml_params_with_macros_override_def_params(self):

        y="""
- def: call_me
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

    def test_yml_params_with_macros2(self):

        y="""
- def: call_me
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

    def test_yml_params_with_macros_and_inheritance(self):

        y="""
- def: METHOD
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

    def test_yml_macros_with_2params(self):

        y="""
- def: call_me
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

    def test_yml_macros_with_2params_embedded(self):

        y="""
- def: call_me
  GET: /{{myvar}}
  params:
    myvar: "{{my}}"

- call: call_me
  params:
    my: bongi
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)
        self.assertEqual( l[0].path, "/{{myvar}}")

        tr=l[0].test( dict(root="http://fake.com") )

        self.assertEqual( tr.res.status, 200)
        self.assertEqual( tr.req.path, "/bongi" )

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
        self.assertRaises(reqman.RMException, lambda: reqman.resolver(["reqman.conf"]))     #not a yaml file

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
            "jack/f1.yml",
            "jack/f2.yml",
            "jack/reqman.conf",
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


#TODO: more tests !!!

if __name__ == '__main__':
    unittest.main()
