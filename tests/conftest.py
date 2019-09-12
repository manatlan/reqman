import pytest
import reqman
import asyncio,sys
import contextlib,io,re,json,html
import tempfile,os,shutil


@pytest.fixture(scope="function")
def Reqs(request):
    def tester(*a,**k):
        return reqman.Reqs(*a,**k)

    yield tester


class FakeExeReturn():
    rc=0
    console=""
    rr=None
    def view(self):
        h=tempfile.mktemp()+".html"
        with open(h,"w+") as fid:
            ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            console=ansi_escape.sub('', self.console)    
            fid.write("""<h3>Test file : "%s"</h3>""" % os.getenv('PYTEST_CURRENT_TEST') )
            fid.write("""<h3>RC : %s <-- "%s"</h3>""" % (self.rc," ".join(sys.argv)))
            fid.write("""<h3>Output Console:</h3><pre>%s</pre>""" % html.escape(console))
            if self.rr:
                fid.write("""<h3>Env:</h3><pre>%s</pre>""" % (json.dumps(self.rr.env, indent=4, sort_keys=True)))
                fid.write("""<h3>Output Html (%s):</h3>%s""" % (self.rr.__class__.__name__,self.rr.html))
            
        import webbrowser
        webbrowser.open_new_tab(h)   

@pytest.fixture(scope="function")
def exe(request):
    def tester(*a,fakeServer=None):
        sys.argv=["reqman.exe"]+list(a)


        f=FakeExeReturn()
        
        print(sys.argv)
        fo,fe = io.StringIO(),io.StringIO()
        with contextlib.redirect_stderr(fe):
            with contextlib.redirect_stdout(fo):
                rc=reqman.main(fakeServer=fakeServer,hookResults=f)

        output=fo.getvalue()+fe.getvalue()
        print(output)

        f.rc=rc
        f.console=output

        return f

    try:
        precdir = os.getcwd()
        dtemp = tempfile.mkdtemp()
        os.chdir( dtemp )

        yield tester

    finally:
        os.chdir( precdir )
        shutil.rmtree(dtemp)    



@pytest.yield_fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
