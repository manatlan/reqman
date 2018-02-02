#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import reqman
import json
from StringIO import StringIO

################################################################## mock
def myhttp(q):
    r=StringIO("the content")
    r.getheaders=lambda: {"content-type":"text/plain","server":"mock"}
    r.status=200
    return reqman.Response(r)

reqman.http = myhttp
##################################################################

class Tests_getVar(unittest.TestCase):

    def test_baba(self):
        env={
            "var":"val",
            "var.x":"valx",
        }
        self.assertEqual( reqman.getVar(env,"nib"), None )
        self.assertEqual( reqman.getVar(env,"var"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )

    def test_baba_dotted(self):
        env={
            "var":dict( ssvar="val" ),
            "var.x":"valx",
        }
        self.assertEqual( reqman.getVar(env,"var.ssvar"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )
        self.assertEqual( reqman.getVar(env,"var.nimp"), None )

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
        self.assertTrue(s)
        self.assertTrue(s)
        self.assertTrue(s)

    def test_env_var_in_path(self):
        env=dict(root="https://github.com/",a_var="explore")

        r=reqman.Req("GET","/{{a_var}}")
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual("content" in s.res.content, True)




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
        f=StringIO(y)
        l=reqman.Reqs(f)
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

        self.assertRaises(reqman.SyntaxException, lambda: reqman.Reqs(f))

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
        f=StringIO(y)
        l=reqman.Reqs(f)
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
        self.assertEqual( json.loads(put.body), {"var": 1, "txt": "{{a_var}}"})
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
        self.assertTrue( "[HTTPS GET /] --> [200]" in str(s))
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, 443)
        self.assertEqual( s.req.path, "/")
        self.assertEqual( s.req.body, None)
        self.assertEqual( s[0],1 )
        self.assertEqual( s[1],1 )

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

        e=reqman.loadEnv( StringIO(conf), ["unknown"] )
        self.assertEqual( e["root"],"AAA" )

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
        self.assertRaises(reqman.ErrorException, lambda: reqman.loadEnv( StringIO(conf) ) )


    def test_yml_exception(self):
        f=StringIO("""
i'm a yaml error
fdsq:
""")
        self.assertRaises(reqman.ErrorException, lambda: reqman.Reqs(f) )

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
        self.assertRaises(reqman.SyntaxException, lambda: reqman.Reqs(StringIO(y)) )



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




#~ class Tests_main(unittest.TestCase):
    #~ def test_env_override_root(self):
        #~ self.assertEqual(reqman.main(["unknown_param","-unknown"]),-1)  # minimal test ;-( ... to increase % coverage


#TODO: more tests !!!
#TODO: test command line !

if __name__ == '__main__':
    unittest.main()
