#!/usr/bin/python
# -*- coding: utf-8 -*-
import reqman
"""
This is the good old reqman tests, in unitest (the cover 94%)
They are not needed (without them, we cover 96% ... with them : 97%)
But they host some functionnal tests that are not covered by pytests ... yet

those tests should be broken down in pytests versions !!!
(SHOULD BE AT THE END, CURRENTLY, COZ THEY ARE DESTRUCTIVE)
"""
import unittest,os,shutil,tempfile,contextlib,inspect,re,json,socket,time
from io import StringIO,BytesIO

fwp = lambda x:x.replace("\\","/") # fake windows path
BINARY = bytes( list(range(255,0,-1)) )


def mockHttp(q):
    if q.path=="/test_cookie":
        return reqman.Response( 200, "the content", {"Content-Type":"text/plain","server":"mock","Set-Cookie":"mycookie=myval"},q.url)
    elif q.path=="/test_binary":
        return reqman.Response( 200, BINARY, {"Content-Type":"audio/mpeg","server":"mock"},q.url)
    elif q.path=="/pingpong":
        return reqman.Response( 200, q.body or "", {"Content-Type":"text/plain","server":"mock"},q.url)
    elif q.path=="/test_json":
        my=dict(
            mydict=dict(name="jack"),
            mylist=["aaa",42,dict(name="john")],
        )
        return reqman.Response( 200, json.dumps(my), {"Content-Type":"application/json","server":"mock"}, q.url)
    elif q.path=="/test_error":
        return reqman.ResponseError( "My Error" )
    elif q.path=="/test_500":
        return reqman.Response( 500, "Server Error", {"Content-Type":"text/plain","server":"mock"}, q.url)
    else:
        return reqman.Response( 200, "the content", {"Content-Type":"text/plain","server":"mock"}, q.url)


###########################################################################
class Tests_CommandLine(unittest.TestCase):
###########################################################################

    def reqman(self,*args):

        fn=inspect.stack()[1][3]


        fo,fe = StringIO(),StringIO()
        with contextlib.redirect_stderr(fe):
            with contextlib.redirect_stdout(fo):
                ret=reqman.main( list(args) )
        txt=fo.getvalue()+fe.getvalue()

        return ret,txt

    def setUp(self):
        self.precdir = os.getcwd()
        self.dtemp = tempfile.mkdtemp()
        os.chdir( self.dtemp )
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp

    def tearDown(self):
        os.chdir( self.precdir )
        shutil.rmtree(self.dtemp)
        reqman.dohttp=self._old

    def create(self,name,content):
        """ create a file in the context dir (see setup/tearDown)"""
        filename=os.path.join(self.dtemp,name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(content)
        return filename

    def test_command_line_bad(self):
        r,o=self.reqman( "unknown_param" )
        self.assertTrue( r==-1)
        self.assertTrue( "ERROR: bad param" in o)

        r,o=self.reqman( "examples","-unknown" )
        self.assertTrue( r==-1)
        self.assertTrue( "ERROR: bad param" in o)


    def test_empty_call(self):
        r,o=self.reqman()
        self.assertEqual( r,-1 )
        self.assertTrue( "USAGE" in o)
        self.assertTrue( reqman.__version__ in o)

    def test_no_scenars_ko(self):
        f=self.create("sub/readme.txt","hello world")

        r,o=self.reqman( "." )
        self.assertEqual( r,-1 )

        r,o=self.reqman( "sub" )
        self.assertEqual( r,-1 )

    def test_bad_yml_syntax(self):
        self.create("scenar.yml","- gfsdgfd\njo:")

        r,o=self.reqman( "." )

        self.assertEqual( r,-1 )
        self.assertTrue( "ERROR: YML syntax" in o)
        self.assertFalse( os.path.isfile("reqman.html") )   # ret==-1 -> no html

    def test_simplest_scenar_yml_scan(self):
        self.create("scenar.yml","GET: http://myserver.com/")

        r,o=self.reqman( "." )

        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz absolute path without reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_simplest_scenar_rml_scan(self):
        self.create("scenar.rml","GET: http://myserver.com/")

        r,o=self.reqman( "." )

        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz absolute path without reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered


    def test_relative_path_without_rc(self):
        self.create("scenar.yml","- GET: /xxxx")

        r,o=self.reqman( "." )

        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "Not callable" in o)               # but not callable, coz relative path without reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_match_patterns(self):
        self.create("s1.yml","- GET: /xxxx")
        self.create("s2.yml","- GET: /xxxx")
        self.create("t1.yml","- GET: /xxxx")

        self.create("tmp/s1.yml","- GET: /xxxx")
        self.create("tmp/s2.yml","- GET: /xxxx")
        self.create("tmp/t2.yml","- GET: /xxxx")

        self.create("tmp/new/z.yml","- GET: /xxxx")

        r,o=self.reqman( "t*.yml" )
        self.assertEqual( o.count("TESTS:"),1)

        r,o=self.reqman( "s*.yml" )
        self.assertEqual( o.count("TESTS:"),2)

        r,o=self.reqman( "s?.yml" )
        self.assertEqual( o.count("TESTS:"),2)

        r,o=self.reqman( "*.yml" )
        self.assertEqual( o.count("TESTS:"),3)

        r,o=self.reqman( "*/*.yml" )
        self.assertEqual( o.count("TESTS:"),3)

        r,o=self.reqman( "*/??.yml" )
        self.assertEqual( o.count("TESTS:"),3)

        r,o=self.reqman( "*/*/*.yml" )
        self.assertEqual( o.count("TESTS:"),1)

        r,o=self.reqman( "*.yml","*/*.yml" )
        self.assertEqual( o.count("TESTS:"),6)

        r,o=self.reqman( "*" )
        self.assertEqual( r,-1)
        self.assertEqual( o.count("YML syntax"),1)




    def test_absolute_path_without_rc(self):
        self.create("scenar.yml","- GET: http://myserver.com/")

        r,o=self.reqman( "." )
        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz absolute path without reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_relative_path_with_rc(self):
        self.create("scenar.yml","- GET: /xxxx")
        self.create("reqman.conf","root: http://myserver.com")

        r,o=self.reqman( "." )

        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz relative path with reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_rc_at_root_and_sub_scenar(self):
        self.create("sub/scenar.yml","- GET: /xxxx")
        self.create("reqman.conf","root: http://myserver.com")

        r,o=self.reqman( "sub" )
        self.assertTrue( "Using 'reqman.conf'" in o)
        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz relative path with reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered


        r,o=self.reqman( "." )
        self.assertTrue( "Using 'reqman.conf'" in o)
        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz relative path with reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_scenar_in_hidden_sub1(self):
        self.create("_sub/scenar.yml","- GET: /xxxx")
        self.create("reqman.conf","root: http://myserver.com")

        r,o=self.reqman( "." )
        self.assertEqual( r,-1 )                #can't be scanned

        r,o=self.reqman( "_sub/scenar.yml" )
        self.assertTrue( "Using 'reqman.conf'" in o)
        self.assertEqual( r,0 )                 # direct ok

    def test_scenar_in_hidden_sub2(self):
        self.create(".sub/scenar.yml","- GET: /xxxx")
        self.create("reqman.conf","root: http://myserver.com")

        r,o=self.reqman( "." )
        self.assertEqual( r,-1 )                #can't be scanned

        r,o=self.reqman( ".sub/scenar.yml" )
        self.assertEqual( r,0 )                 # direct ok

    def test_scenar_with_another_ext(self):
        self.create("scenar.txt","- GET: /xxxx")
        self.create("reqman.conf","root: http://myserver.com")

        r,o=self.reqman( "." )
        self.assertEqual( r,-1 )

        r,o=self.reqman( "scenar.txt" )
        self.assertEqual( r,0 )                             # all is ok
        self.assertTrue( "200" in o)                        # but callable, coz relative path with reqman.conf
        self.assertTrue( os.path.isfile("reqman.html") )    # a html is rendered

    def test_reqman_rendering_stdout_and_html(self):
        self.create("scenar.rml","- GET: http://kif.nimp/\n"*3 + "- GET: http://error.com/test_500")
        r,o=self.reqman( "." )
        self.assertEqual( r,0 )                             # all is ok
        self.assertEqual( o.count("-->"),4 )                # 4 req

        with open("reqman.html","r") as fid:
            buf=fid.read()
        self.assertEqual( buf.count("<b>GET</b>"), 4)
        self.assertTrue( "<title>Result: 0/0</title>" in buf)

        r,o=self.reqman( "--ko","." )
        self.assertEqual( r,0 )                             # all is ok
        self.assertEqual( o.count("-->"),0 )                # "not failed" so no displayed

    def test_reqman_rendering_tests(self):
        s="""
- GET: http://kif.nimp/
  tests:
     - status: 200
     - server: mock

- GET: http://kif.nimp2/
  tests:
     - status: 222
     - server: mock
"""
        self.create("scenar.rml",s)

        r,o=self.reqman( "." )
        self.assertEqual( r,1 )                             # 1 test failed !
        self.assertEqual( o.count("-->"),2 )                # 2 reqs!
        self.assertTrue("RESULT" in o)
        self.assertTrue("3/4" in o)

        r,o=self.reqman( ".","--ko" )
        self.assertEqual( r,1 )                             # 1 test failed !
        self.assertEqual( o.count("-->"),1 )                # 2 reqs, but one is displayed
        self.assertTrue("RESULT" in o)
        self.assertTrue("3/4" in o)


    def test_reqman_USAGE_with_rc(self):
        self.create("reqman.conf","""
root: http://site1.com

toto:
    root: http://site2.com
        """)
        r,o=self.reqman()

        self.assertTrue( "Using 'reqman.conf'" in o)
        self.assertEqual( r,-1 )
        self.assertTrue( "USAGE" in o)
        self.assertTrue( reqman.__version__ in o)
        self.assertTrue( "http://site1.com" in o)
        self.assertTrue( "http://site2.com" in o)


        # we make a subfolder "sub"
        self.create("sub/readme.txt","hello world")


        # try with sub folder
        r,o=self.reqman("sub")

        self.assertTrue( "Using 'reqman.conf'" in o)
        self.assertEqual( r,-1 )
        self.assertTrue( "USAGE" in o)
        self.assertTrue( reqman.__version__ in o)
        self.assertTrue( "http://site1.com" in o)
        self.assertTrue( "http://site2.com" in o)


        #go in "sub" dir
        os.chdir("sub")

        # without params
        # reqman will search the rc in backyards
        r,o=self.reqman()
        self.assertTrue( re.search("Using '\.\..reqman\.conf'", o ) )
        self.assertEqual( r,-1 )
        self.assertTrue( "USAGE" in o)
        self.assertTrue( reqman.__version__ in o)
        self.assertTrue( "http://site1.com" in o)
        self.assertTrue( "http://site2.com" in o)

        # try with scan .
        # reqman will search the rc in backyards
        r,o=self.reqman(".")

        self.assertTrue( re.search("Using '\.\..reqman\.conf'", o ) )
        self.assertEqual( r,-1 )
        self.assertTrue( "USAGE" in o)
        self.assertTrue( reqman.__version__ in o)
        self.assertTrue( "http://site1.com" in o)
        self.assertTrue( "http://site2.com" in o)

    def test_reqman_multiple_switch(self):
        self.create("reqman.conf","""
root: http://localhost

folder: fo1
file: fi1

overfo:
    folder: fo2
    root: http://server

overfi:
    file: fi2
        """)
        self.create("scenar.rml","GET: /{{folder}}/{{file}}")

        r,o=self.reqman(".")
        self.assertTrue( "/fo1/fi1" in o)

        r,o=self.reqman(".","-overfo")
        self.assertTrue( "/fo2/fi1" in o)

        r,o=self.reqman(".","-overfo","-overfi")
        self.assertTrue( "/fo2/fi2" in o)

        r,o=self.reqman()
        self.assertTrue( "http://localhost" in o)   # root is displayed in usage
        self.assertTrue( "overfo" in o)              # but root switch are here too
        self.assertTrue( "overfi" not in o)          # but non-root switch not

    def test_reqman_create(self):
        r,o=self.reqman("new","https://jkif.com:80/action?state=a")
        self.assertFalse( "Using" in o)
        self.assertTrue( "Create reqman.conf" in o)
        self.assertTrue( "Create 0010_test.rml" in o)

        r,o=self.reqman("new","https://willBeLost:99/action?state=b")
        self.assertTrue( "Using" in o)
        self.assertTrue( "Create 0020_test.rml" in o)

        r,o=self.reqman(".")
        self.assertTrue( "./0010_test.rml" in o)
        self.assertTrue( "./0020_test.rml" in o)
        self.assertTrue( o.count("-->")==2)
        self.assertTrue( "2/2" in o)

        with open("reqman.html","r") as f: h=f.read()
        self.assertTrue( "GET https://jkif.com:80/action?state=a" in h)
        self.assertTrue( "GET https://jkif.com:80/action?state=b" in h)
        self.assertFalse( "GET https://willBeLost:99/action?state=b" in h)  # full url will be lost ;-( (coz root/rc is already defined)

    def test_reqman_create_bad(self):
        r,o=self.reqman("new","not_an_url")
        self.assertEqual(r,-1)
        self.assertFalse( "Using" in o)
        self.assertTrue("you shoul provide a full url",o)

    def test_reqman_create_in_sub_and_existing_rc_up(self):
        self.create("reqman.conf","""root: http://localhost""")
        self.create("sub/readme.txt","""just for create this dir""")
        os.chdir("sub")

        r,o=self.reqman("new","not_an_url")
        self.assertEqual(r,0)
        self.assertTrue( "Using" in o)
        self.assertTrue( "Create 0010_test.rml" in o)
        self.assertFalse( "Create reqman.conf" in o)

    def test_scenar_tests_in_list_or_dict(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: {"result":[1,2]}
  tests:                                    # original/better form
    - status: 200
    - content: result

- POST: http://jo/pingpong
  body: {"result":[1,2]}
  tests:                                    # accepted form
    status: 200
    content: result
""")
        r,o=self.reqman(".")
        self.assertTrue( "***WARNING*** 'tests:' should be a list" in o )   # a warn is displayed
        self.assertTrue( o.count("OK")==4)          # all is ok

    def test_scenar_headers_in_list_or_dict(self):
        self.create("scenar.rml","""
- GET: http://jo/
  headers:                                  # original/better form
    content-type: text/plain
    message: hello

- GET: http://jo/
  headers:                                  # accepted form
    - content-type: text/plain
    - message: hello
""")
        r,o=self.reqman(".")
        self.assertTrue( "***WARNING*** 'headers:' should be filled" in o )   # a warn is displayed
        self.assertTrue( o.count("-->")==2)          # all req are ok

    def test_json_match_all_any(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: {"result":[1,2]}
  tests:
    - json.result.size: 2
    - json.result.0: 1
    - json.result.1: 2
    - json.result: [1,2]        #match All !
    - json.result:              #match All !
        - 1
        - 2
    - json.result:              #match Any !
        - [1,2]
        - "kkkk"


- POST: http://jo/pingpong
  body: {"result":1}
  tests:
    - json.result: [1,2]        #match any !
    - json.result:              #match any !
        - 1
        - 2

""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==8)          # all is ok

    def test_json_compare_dict_list(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: |
    {
        "a_dict": {"z":true,"a":1,"b":{"x":12,"s":1.1},"c":[1,2,3],"d":null},
        "a_list": [1,2,false,null,99,0.5]
    }
  tests:
    - json.a_dict:  {"z":true,"a":1,"b":{"x":12,"s":1.1},"c":[1,2,3],"d":null}
    - json.a_list:  [1,2,false,null,99,0.5]

""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==2)          # all is ok


    def test_content_matchs(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: |
    {
        "a_list": [1, 2, false, null, 99, 0.5],
        "a_dict": {"z":true, "a":1, "b": {"x":12,"s":1.1}, "c": [1,2,3],"d": null}
    }
  tests:
    - content: |
        {
            "a_dict" : {"d":null,"z":true,"a":1,"b":{"s":1.1,"x":12},"c":[1,2,3]},
            "a_list" : [1,2,false,null,99,0.5]
        }

""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==1)          # all is ok

        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: [1,2]
  tests:
    - content:
        - 1
        - 2
""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==1)          # all is ok


        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: bla bla kiki top
  tests:
    - content: kiki                 # control partial content
    - content:                      # list of control partial content
        - blo
        - bla
        - pot
    - content: bla bla kiki top     # full compare
""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==3)          # all is ok

    def test_tests_compare_operators(self): # only json.* & status !
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: {"v":42}
  tests:
    - json.v: 42            # \
    - json.v: .=42          #  |---> that's (EXACTLY) the same !!!
    - json.v: .==42         # /

    - json.v: .!=12
    - json.v: .>12
    - json.v: .<62
    - json.v: .>=42
    - json.v: .<=42

    - status: .!=400
    - status: .<201
    - status: .>=200

    - status: . =200
    - status: . = 200
""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==12)          # all is ok

        self.create("scenar.rml","""
- GET: http://jo/kif
  tests:
    - status: kokoko
    - status: .={'kkko':78}
    - status: .={kkko:78}
    - status: .!>10                     # use < !
    - status: .!!=12
    - status: ..=200
    - status: .!={xxx]
""")
        r,o=self.reqman(".")
        self.assertEqual( r,7 )                     # 0 error !
        self.assertTrue( o.count("KO")==7)          # all is ok

        self.create("scenar.rml","""
- proc:
    GET: http://jo/kif
    tests:
        - status: .!=<<vmax>>
        - status: .><<vmin>>
        - status: .<<<vmax>>        # triple < !!
- call: proc
  params:
    vmax: 400
    vmin: 150
""")
        r,o=self.reqman(".")
        self.assertTrue( r==0 )                     # 0 error !
        self.assertTrue( o.count("OK")==3)          # all is ok

    def test_content_ambiguity_trouble_fixed(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: { result: true }
  tests:
     - status: 200
     - content: "true"
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==2)          # all is ok

    def test_matchAny_in_status(self):
        self.create("scenar.rml","""
- GET: http://jo/kif
  tests:
     - status:
         - . < 300
         - 400
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==1)          # all is ok

    def test_foreach(self):
        self.create("scenar.rml","""
- GET: http://jo/<<val2>>/<<val>>
  foreach:
    - val: 1
    - val: 2
    - val: 3
  params:
    val2: hello
  tests:
     - status: 200
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==3)          # all is ok

    def test_foreach(self):
        self.create("scenar.rml","""
- POST: http://jo/pingpong
  body: <<val>>
  foreach:
    - val: { 'ret': 'hello1' }
    - val: { 'ret': 'hello2' }
    - val: { 'ret': 'hello3' }
  tests:
     - status: 200
     - json.ret: <<val.ret>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==6)          # all is ok



    def test_foreach_call(self):
        self.create("scenar.rml","""
- proc:
    GET: http://jo/<<val2>>/<<val>>
    tests:
        - status: 200
    params:
      val2: hello
- call: proc
  foreach:
    - val: 1
    - val: 2
    - val: 3
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )                     # 0 error !
        self.assertTrue( o.count("OK")==3)          # all is ok


    def test_bad_foreach_dynamic_call(self):
        self.create("reqman.conf","""liste: [1,2,3]""")
        self.create("scenar.rml","""
- GET: http://jo/
  tests:
    - status: 200
  params: <<liste>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue("params is not a dict" in o)

    def test_ok_foreach_dynamic_replace(self):
        self.create("reqman.conf","""root: http://jo/\nkif: /2""")
        self.create("scenar.rml","""
- GET: <<path>>
  tests:
    - status: 200
  foreach:
    - path: /1
    - path: <<kif>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==2)          # all is ok

    def test_ok_foreach_dynamic_call1(self):
        self.create("scenar.rml","""
- proc:
      GET: http://jo/<<v1>>/<<v2>>/<<val>>
      tests:
        - status: 200
      params:
        v1: 1

- call: proc
  foreach: <<liste>>
  params:
    liste:
        - val: 1
        - val: 2
        - val: 3
    v2: 2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==3)          # all is ok

    def test_ok_foreach_dynamic_call2(self):    # the more complex exemple !!!!!!!
        self.create("scenar.rml","""
- proc:
      GET: http://jo/<<v1>>/<<v2>>/<<val>>/<<v>>
      tests:
        - status: 200
      params:
        v1: 1
      foreach:
        - v: a
        - v: b

- call: proc
  foreach: <<3|mkliste>>
  params:
    mkliste: return x*[{'val':1},{'val':2},{'val':3}]
    v2: 2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==18)          # all is ok

    def test_foreach_in_foreach(self):
        self.create("scenar.rml","""
- proc:
        GET: http://jo/<<path1>>/<<path2>>
        foreach:
            - path2: a
            - path2: b
        tests:
            - status: 200
- call: proc
  foreach:
    - path1: a
    - path1: b
  tests:
    - content-type: text
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==8)          # all is ok

    def test_bad_yml_multiple_action(self):
        self.create("scenar.rml","""
- GET: http://jo/
  POST: http://jo/
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action or too many" in o)          # all is ok

    def test_bad_yml_multiple_same_action(self):
        self.create("scenar.rml","""
- GET: http://s/jim
  GET: http://s/jack        # it overrides ^^
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( "/jack" in o)          # all is ok

    def test_invalid_keys(self):
        self.create("scenar.rml","""
- GET: http://s/jim
  kiki: kkk
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "Not a valid entry" in o)

        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
  kiki: kkk
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action or too many" in o)

        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
  body: kkk
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action or too many" in o)

        self.create("scenar.rml","""
- kif: http://s/jim
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action or too many" in o)

        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
- call: proc
  body: kkk
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "Not a valid entry" in o)

        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
- call: proc
  kiki: kkk
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "Not a valid entry" in o)

    def test_call_dynamic(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
- call: <<2|list>>
  params:
    list: return x * ['proc','proc']
  tests:
    status: 200
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==4)          # all is ok

    def test_call_dynamic_inside(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim
- call:
    - proc
    - <<pro>>
  params:
    pro: proc
  tests:
    status: 200
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==2)          # all is ok

    def test_foreach_dynamic_inside(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/jim/<<v>>
- call: [proc,proc]
  foreach:
    - v: 1
    - <<noob>>
  params:
    noob:
        v: 2
  tests:
    status: 200
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==4)          # all is ok

    def test_dynamic_status(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/<<path>>
      tests:
        - status: <<st>>
- call: proc
  foreach:
    - st: 200
      path: v1
    - st: 200
      path: v2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( o.count("OK")==2)          # all is ok

    def test_BAD_call_bad_action_inside_proc(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/<<path>>
    - hgfdhgf
- call: proc
  foreach:
    - path: v1
    - path: v2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action" in o)

    def test_BAD_call_bad_action_inside_proc(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/<<path>>
    - hgfdhgf: kkkk
- call: proc
  foreach:
    - path: v1
    - path: v2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "no action" in o)

    def test_BAD_call_bad_action_inside_proc(self):
        self.create("scenar.rml","""
- proc:
    - GET: http://s/<<path>>
    - tests:                      # he can believe that's a proc
        - status: 9999
- call: proc
  foreach:
    - path: v1
    - path: v2
""")
        r,o=self.reqman(".")
        self.assertEqual( r,-1 )
        self.assertTrue( "procedure can't be named" in o)

    def test_multi_save_inherits(self):
        self.create("scenar.rml","""
- proc:
    - POST: http://s/pingpong
      body: 42
      save: var1
- call: proc
  save: var2
- GET: /jo1/<<var1>>
- GET: /jo2/<<var2>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( "/jo1/42" in o)
        self.assertTrue( "/jo2/42" in o)
        self.assertTrue( o.count("Not callable")==2)

    def test_multi_save_inherits2(self):
        self.create("scenar.rml","""
- proc:
    - POST: http://s/pingpong
      body: 42
      save:
        - var1
        - var3
- call: proc
  save: var2
- GET: /jo1/<<var1>>
- GET: /jo2/<<var2>>
- GET: /jo3/<<var3>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( "/jo1/42" in o)
        self.assertTrue( "/jo2/42" in o)
        self.assertTrue( "/jo3/42" in o)
        self.assertTrue( o.count("Not callable")==3)

    def test_multi_save_inherits3(self):
        self.create("scenar.rml","""
- proc:
    - POST: http://s/pingpong
      body: 42
      save: var1
- call: proc
  save:
    - var2
    - var3
- GET: /jo1/<<var1>>
- GET: /jo2/<<var2>>
- GET: /jo3/<<var3>>
""")
        r,o=self.reqman(".")
        self.assertEqual( r,0 )
        self.assertTrue( "/jo1/42" in o)
        self.assertTrue( "/jo2/42" in o)
        self.assertTrue( "/jo3/42" in o)
        self.assertTrue( o.count("Not callable")==3)

    def test_http_error(self):
        self.create("scenar.rml","""
- GET: http://s/test_error
  tests:
    - status: null
    - status: .>=100
    - status: .>100
    - status: .<=100
    - status: .<100
    - status: .=100
    - status: .!=100
""")
        r,o=self.reqman(".")
        # self.assertEqual( r,0 )
        # self.assertTrue( "/jo1/42" in o)
        # self.assertTrue( "/jo2/42" in o)
        # self.assertTrue( "/jo3/42" in o)
        # self.assertTrue( o.count("Not callable")==3)


#     @only
#     def test_tuto(self): # only json.* & status !
#         self.create("scenar.rml","""
# - proc1:                   # this is a declaration !
#     - proc2:               # this is a sub declaration !
#       - GET: /nib
#     - call:               # Call can be a list of procedures to call !!!
#       - proc2
#       - proc2

# - call: proc1  # this will produce 2 gets !
# """)
#         r,o=self.reqman(".")
#         print(o)


class Tests_resolver_with_rc(unittest.TestCase):        # could be replaced with Tests_CommandLine

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
        self.assertEqual( len(ll),1 )

    def test_rc2(self):
        rc,ll = reqman.resolver(["jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEqual( len(ll),1 )
    

class Tests_resolver_without_rc(unittest.TestCase): # could be replaced with Tests_CommandLine

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
        self.assertEqual( len(ll),1 )

    def test_rc2(self):
        rc,ll = reqman.resolver(["jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEqual( len(ll),1 )

    def test_rc3(self):
        rc,ll = reqman.resolver(["jo/f1.yml","jack/f1.yml"])
        self.assertTrue( "jack/reqman.conf" in fwp(rc) )
        self.assertEqual( len(ll),2 )
        self.assertEqual( ll,['jack/f1.yml', 'jo/f1.yml'] )    # sorted

    #~ @only
    def test_rml(self):
        rc,ll = reqman.resolver(["jim/f1.rml"])
        self.assertTrue( "jim/reqman.conf" in fwp(rc) )
        self.assertEqual( len(ll),1 )

class Tests_TRANSFORM(unittest.TestCase):

    def setUp(self):
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp
    def tearDown(self):
        reqman.dohttp=self._old
        
    def test_trans_var(self):
        env=dict(
            root="https://github.com/",
            trans="return x*2",
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
        self.assertEqual(s.req.body,"hellohello")

    def test_trans_chainable(self):
        env=dict(
            root="https://github.com/",
            trans="return x*2",
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
        self.assertEqual(s.req.body,"hellohellohellohello")


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


class Tests_params_NEW(unittest.TestCase):

    def setUp(self):
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp
    def tearDown(self):
        reqman.dohttp=self._old


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

        self.assertEqual( tr.req.body, "line1\nline2\nline3\n" )

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

        self.assertEqual( tr.req.body, "startline1\nline2\nline3\nend" )

    def test_yml_params_escape_string3(self):

        y="""
- POST: /test
  body:
    start<<myvar>>end
"""
        l=reqman.Reqs(StringIO(y))
        self.assertEqual( len(l), 1)

        tr=l[0].test({"myvar":"aaa\nbbb"})

        self.assertEqual( tr.req.body, "startaaa\nbbbend" )


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

        self.assertEqual( tr.req.body, "start\naaa\nbbb\nend\n" )

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






class Tests_env_save(unittest.TestCase):
    def setUp(self):
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp
        if os.path.isfile("aeff.txt"):
            os.unlink("aeff.txt")

    def tearDown(self):
        reqman.dohttp=self._old
        if os.path.isfile("aeff.txt"):
            os.unlink("aeff.txt")

    def test_create_var(self):
        f=StringIO("""
- GET: http://supersite.fr/rien
  save: newVar
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)

        self.assertEqual( env, {'newVar': 'the content'} )

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
        self.assertEqual( env, {'newVar': 'old value'} )
        l[0].test(env)
        self.assertEqual( env, {'newVar': 'the content'} )

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



    def test_save_var_to_file_denied(self):  # Works on Windows ;-(
        f=StringIO("""
- GET: http://supersite.fr/rien
  save: file:///nimp/nawak/unknown/path/to/nowhere
""")
        l=reqman.Reqs(f)

        env={}
        self.assertRaises(reqman.RMException, lambda: l[0].test(env))


#     def test_save_var_to_file_txt(self):
#         f=StringIO("""
# - GET: http://supersite.fr/
#   save: file://aeff.txt
# """)
#         l=reqman.Reqs(f)

#         env={}
#         self.assertFalse( os.path.isfile("aeff.txt") )
#         l[0].test(env)

#         self.assertTrue( os.path.isfile("aeff.txt") )

#         with open("aeff.txt") as fid:
#             content=fid.read()

#         self.assertEqual( content, "the content" )

#     def test_save_var_to_file_bin(self):
#         f=StringIO("""
# - GET: http://supersite.fr/test_binary
#   save: file://aeff.txt
# """)
#         l=reqman.Reqs(f)

#         env={}
#         self.assertFalse( os.path.isfile("aeff.txt") )
#         l[0].test(env)

#         self.assertTrue( os.path.isfile("aeff.txt") )

#         with open("aeff.txt","rb") as fid:
#             content=fid.read()
#         self.assertEqual( content, BINARY )

    def test_save_var_to_multiple(self):
        f=StringIO("""
- justdoit:
    GET: http://supersite.fr/rien
    save:
        - var1
        - var2

- call: justdoit
""")
        l=reqman.Reqs(f)

        env={}
        l[0].test(env)
        self.assertEqual( env["var1"], 'the content' )
        self.assertEqual( env["var2"], 'the content' )




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


class Tests_Reqs(unittest.TestCase):

    def setUp(self):
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp
    def tearDown(self):
        reqman.dohttp=self._old

    def test_simplest_yml(self):
        f=StringIO("GET: https://github.com/")
        l=reqman.Reqs(f)
        self.assertEqual( len(l), 1)

    def test_encoding_yml(self):
        f=StringIO("GET: https://github.com/\nbody: héhé")
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),str)

        f= BytesIO( u"GET: https://github.com/\nbody: héhé".encode("utf-8") )
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),str)

        f=BytesIO( u"GET: https://github.com/\nbody: héhé".encode("cp1252") )
        l=reqman.Reqs(f)
        self.assertEqual( type(l[0].body),str)


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

        reqman.COOKIEJAR = reqman.CookieStore()
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
        self.assertEqual( post.headers, {})

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
    - CoNtEnt-tYpE:         application/json
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

    def test_yml_tests_list(self):

        y="""
- GET: /test_json
  tests:
    - content-type:
        - application/json
        - application/text
    - json.mydict.name:
        - jack
        - jim
    - status:
        - 200
        - 201
"""
        f=StringIO(y)
        l=reqman.Reqs(f)

        s=l[0].test( dict(root="https://github.com:443/"))
        self.assertTrue( all(s) )

    def test_yml_tests_list_substitutes(self):

        s="""
- GET: /test_json
  tests:
    - content-type:
        - <<p1>>
        - "{{p2}}"
    - content: <<p1>>
  params:
    p1: application
    p2: json
    p3: john
"""
        l=reqman.Reqs(StringIO(s))
        self.assertTrue( {'content': '<<p1>>'} in l[0].tests )
        self.assertTrue( {'content-type': ['<<p1>>', '{{p2}}']} in l[0].tests, )

        t=l[0].test( dict(root="https://github.com:443/"))
        self.assertTrue( all(s) ) # ensure all tests are substitued (and match results)


class Tests_Req(unittest.TestCase):
    def setUp(self):
        self._old = reqman.dohttp
        reqman.dohttp = mockHttp
    def tearDown(self):
        reqman.dohttp=self._old

    def test_noenv(self):
        r=reqman.Req("get","https://github.com/")
        s=r.test()
        self.assertEqual(s.res.status, 200)
        self.assertTrue(s.res.time != None)

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

    def test_var_complex_transform_in_call(self):
        f=StringIO("""
- context:
    - proc:
        - POST: /<<var>>

    - call: proc
      params:
        var: <<kif|dd>>

- call: context
  params:
     kif: "a,b"
     dd: return "/".join(x.split(","))

""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, '/a/b' )

    def test_var_complex_transform_in_call2(self): # a real case I met ;-)
        f=StringIO("""
- context:
    - proc:
        - POST: /<<var|dd>>          # <-- the |dd is here

    - call: proc
      params:
        var: <<kif>>                 # <-- not here

- call: context
  params:
     kif: "a,b"
     dd: return "/".join(x.split(","))

""")
        l=reqman.Reqs(f)

        env={}
        s=l[0].test(env)
        self.assertEqual( s.req.path, '/a/b' )


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


class Tests_CookieStore(unittest.TestCase):

    def test(self):
        import http.cookies
        CJ=reqman.CookieStore()

        #------------------------------------------------------ create a cookie using "Cookie"
        c = http.cookies.SimpleCookie()
        c["cidf"]="malz"
        c["cidf"]["path"]="/yo"

        c["cidf2"]="malz2"
        headers=[ ("user-Agent","yo"),("content-type","text/html") ]
        for k,v in c.items():
            headers.append(tuple(v.output().split(": ",1)))
        #------------------------------------------------------

        CJ.saveCookie(headers,'http://localhost')

        self.assertEqual( CJ.getCookieHeaderForUrl('http://localhost/yo') , {'Cookie': 'cidf=malz; cidf2=malz2'} )
        self.assertEqual( CJ.getCookieHeaderForUrl('http://localhost/') , {'Cookie': 'cidf2=malz2'} )
        self.assertEqual( CJ.getCookieHeaderForUrl('http://mama.com/') , {} )

        CJ.saveCookie( {"set-cookie":"kkk=va"},'http://mama.com')
        self.assertEqual( CJ.getCookieHeaderForUrl('http://mama.com/') , {'Cookie': 'kkk=va'} )

class Tests_transform(unittest.TestCase):

    def test_b_aba(self):
        env={
            "var": "hello",
            "trans": "return x and x*2",
        }
        self.assertEqual( reqman.transform("xxx",env,"trans"), "xxxxxx" )
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
        self.assertRaises(reqman.RMNonPlayable, lambda: reqman.getVar(env,"nib") )
        self.assertEqual( reqman.getVar(env,"var"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )
        self.assertEqual( reqman.getVar(env,"mylist.0"), 31 )
        self.assertEqual( reqman.getVar(env,"mylist.1"), 32 )
        self.assertEqual( reqman.getVar(env,"mylist.2"), 33 )
        self.assertRaises(reqman.RMNonPlayable, lambda: reqman.getVar(env,"mylist.3") )

    def test_baba_dotted(self):
        env={
            "var":dict( ssvar="val",x="eclipsed" ),
            "var.x":"valx", #this is a var named "var.x" !!
        }
        self.assertEqual( reqman.getVar(env,"var.ssvar"), "val" )
        self.assertEqual( reqman.getVar(env,"var.x"), "valx" )
        self.assertRaises(reqman.RMNonPlayable, lambda: reqman.getVar(env,"var.nimp") )
        self.assertRaises(reqman.RMNonPlayable, lambda: reqman.getVar(env,"xxx") )


    def test_baba_trans(self):
        env={
            "var": "hello",
            "trans": "return x*2",
        }
        self.assertEqual( reqman.getVar(env,"var"), "hello" )
        self.assertEqual( reqman.getVar(env,"var|trans"), "hellohello" )
        self.assertRaises(reqman.RMException, lambda: reqman.getVar(env,"var|unknown") )


class Tests_content(unittest.TestCase):

    def test_content(self):
        x=reqman.Content("ooo")
        self.assertEqual( str(x), "ooo" )
        self.assertTrue( "o" in x )
        self.assertEqual( x.toBinary(), b"ooo" )
        self.assertTrue( "o" in x )

        x=reqman.Content(b"ooo")
        self.assertEqual( str(x), "ooo" )
        self.assertTrue( "o" in x )
        self.assertEqual( x.toBinary(), b"ooo" )
        self.assertTrue( "o" in x )

        x=reqman.Content("oéo")
        self.assertEqual( str(x), "oéo" )
        self.assertTrue( "é" in x )
        self.assertEqual( x.toBinary(), bytes("oéo","utf8") )
        self.assertTrue( "é" in x )

        x=reqman.Content( BINARY )
        self.assertTrue( "BINARY SIZE" in x )
        self.assertEqual( x.toBinary(), BINARY )

    def test_content_encoded(self):
        b=bytes("oéo","utf8")
        x=reqman.Content( b )
        self.assertEqual( x.toBinary(), b )
        self.assertEqual( str(x), "oéo" )
        self.assertTrue( "é" in x )

        b=bytes("oéo","cp1252")
        x=reqman.Content( b )
        self.assertEqual( x.toBinary(), b )
        self.assertEqual( str(x), "oéo" )
        self.assertTrue( "é" in x )



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


