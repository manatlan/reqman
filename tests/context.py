#!/usr/bin/python
# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,tempfile,shutil
sys.path.append( os.path.dirname(os.path.dirname(__file__)) )
import reqman
import pytest,contextlib
from io import StringIO





    

@pytest.fixture(scope="module")
def client(request):
    files = getattr(request.module, "FILES", [])    # get files from test_.*.py file
    server = getattr(request.module, "SERVER", {})   

    precdir = os.getcwd()
    dtemp = tempfile.mkdtemp()
    os.chdir( dtemp )

    for file in files:
        filename=os.path.join(dtemp,file["name"])
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(file["content"])

    def tester(*args):
        class Ret():pass
        r=Ret()

        if os.path.isfile("reqman.html"):
            os.unlink("reqman.html")

        print("\n> reqman.exe"," ".join(args))
        fo,fe = StringIO(),StringIO()
        with contextlib.redirect_stderr(fe):
            with contextlib.redirect_stdout(fo):
                r.code=reqman.main( list(args) )
        r.console=fo.getvalue()+fe.getvalue()
        print(r.console)
        
        if os.path.isfile("reqman.html"):
            with open("reqman.html") as fid:
                r.html=fid.read()
        else:
            r.html=None
        r.inproc=reqman.main
        return r

    reqman_http = reqman.dohttp

    def mockHttp(q):
        hq="%s %s" % (q.method,q.url)
        if hq in server:
            params={"url":q.url,"headers":{}}
            params.update( server[hq](q) )
            return reqman.Response( **params )
        else: # real world
            return reqman_http(q)

    reqman.dohttp = mockHttp
    yield tester
    reqman.dohttp = reqman_http

    os.chdir( precdir )
    shutil.rmtree(dtemp)
