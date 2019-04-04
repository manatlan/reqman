#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,tempfile,shutil,sys
sys.path.append( os.path.dirname(os.path.dirname(__file__)) )
import reqman
import pytest,contextlib
from io import StringIO




#===============================================
def runServerMockWith(server):
    def mockHttp(q):
        if q.path in server:
            mock=server[q.path]
        elif q.url in server:
            mock=server[q.url]
        else:
            mock=None

        if mock:
            if callable(mock): mock=mock(q)

            if len(mock)==2:
                status,body=mock
                headers={"Content-Type":"text/plain","server":"mock"}
            elif len(mock)==3:
                status,body,headers=mock
            return reqman.Response( status, body, headers, q.url, "MOCK %s" % status)
        else:
            return reqman.Response( 404, "Not Found (fixture)", {"Content-Type":"text/plain","server":"mock"}, q.url,"MOCK 404")
    return mockHttp
#===============================================

    

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
        class Ret():
            code=None
            console=None
            html=None
            inproc=None
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
    reqman.dohttp = runServerMockWith(server)
    yield tester
    reqman.dohttp = reqman_http

    os.chdir( precdir )
    shutil.rmtree(dtemp)


@pytest.fixture(scope="function")
def reqs(request):
    server = getattr(request.module, "SERVER", {})   

    def caller(txt,env=None):
        return reqman.Reqs( StringIO(txt),env )

    precdir = os.getcwd()
    os.chdir( tempfile.mkdtemp() )

    prechttp = reqman.dohttp
    reqman.dohttp = runServerMockWith(server)
    yield caller
    reqman.dohttp=prechttp

    os.chdir( precdir )





