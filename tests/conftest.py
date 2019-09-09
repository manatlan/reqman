import pytest
import reqman
import asyncio,sys
import contextlib,io
import tempfile,os,shutil

@pytest.fixture(scope="function")
def Reqs(request):
    def tester(*a,**k):
        return reqman.Reqs(*a,**k)

    yield tester

@pytest.fixture(scope="function")
def exe(request):
    def tester(*a,fakeServer=None):
        sys.argv=["reqman.exe"]+list(a)

        print(sys.argv)
        fo,fe = io.StringIO(),io.StringIO()
        with contextlib.redirect_stderr(fe):
            with contextlib.redirect_stdout(fo):
                rc=reqman.main(fakeServer=fakeServer)

        output=fo.getvalue()+fe.getvalue()
        print(output)

        class FakeExeReturn(): pass
        
        f=FakeExeReturn()
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
