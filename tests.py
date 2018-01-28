#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import reqman
import json
from StringIO import StringIO

################################################################## mock
def myhttp(q):
    r=StringIO("the content")
    r.getheaders=lambda: {"content-type":"plain/text","server":"mock"}
    r.status=200
    return reqman.Response(r)

reqman.http = myhttp
##################################################################

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

        r=reqman.Req("GET","/",tests=[dict(status=200),dict(content="content"),dict(server="mock")])
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual( len(s), 3)
        self.assertEqual(s[0][1], True)
        self.assertEqual(s[1][1], True)
        self.assertEqual(s[2][1], True)

    def test_env_var_in_path(self):
        env=dict(root="https://github.com/",a_var="explore")

        r=reqman.Req("GET","/{{a_var}}")
        s=r.test(env)
        self.assertEqual(s.res.status, 200)
        self.assertEqual("content" in s.res.content, True)


class Tests_Reqs(unittest.TestCase):

    def test_simplest_yml(self):
        f=StringIO("GET: https://github.com/")
        f.name="yo"
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 1)


    def test_yml(self):
        y="""
- GET: https://github.com/
- PUT: https://github.com/explore
- DELETE: https://github.com/explore
- POST: https://github.com/explore
"""
        f=StringIO(y)
        f.name="filename"
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 4)
        self.assertEqual( [i.method for i in l], ['GET', 'PUT', 'DELETE', 'POST'])

    def test_bad_yml(self):
        f=StringIO("")
        f.name="filename"

        self.assertEqual(reqman.Reqs(f),[])

    def test_bad_yml2(self):
        y="""
- NOOP: https://github.com/
"""
        f=StringIO(y)
        f.name="filename"

        self.assertRaises(reqman.SyntaxException, lambda: reqman.Reqs(f))

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
        f=StringIO(y)
        f.name="filename"
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
        self.assertEqual( s.req.data, None)
        self.assertEqual( s.req.headers,  {'h1': 'my h1', 'h2': 'my h2'})

        s=post.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, None)
        self.assertEqual( s.req.path, "/explore")
        self.assertEqual( s.req.data, "explore")
        self.assertEqual( s.req.headers,  {'h1': 'my h1'})

        s=put.test(env)
        self.assertEqual( s.req.host, "github.com")
        self.assertEqual( s.req.protocol, "https")
        self.assertEqual( s.req.port, None)
        self.assertEqual( s.req.path, "/")
        self.assertEqual( json.loads(s.req.data), {"var": 1, "txt": "explore"})
        self.assertEqual( s.req.headers,  {'h1': 'my h1',"h3":"explore"})

#TODO: more tests !!!

if __name__ == '__main__':
    unittest.main()

