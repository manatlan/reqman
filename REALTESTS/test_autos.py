import sys,os,io,contextlib
from glob import glob
import pytest
import fakereqman, reqman
import os,tempfile,shutil

WS=None
def setup_module():
    global WS
    WS=fakereqman.FakeWebServer(11111)
    WS.start()
    import time
    time.sleep(1)   


def teardown_module():
    global WS
    WS.stop()

@pytest.mark.parametrize('file', glob( os.path.join( os.path.dirname(__file__),"auto_*.yml")) + glob( os.path.join( os.path.dirname(__file__),"auto_*/*.yml")) )
def test_file(file):
    try:
        precdir = os.getcwd()
        testdir = tempfile.mkdtemp()
        os.chdir( testdir )

        err=run(file)
        assert err=="", "File '%s' : %s" % (file,err)

    finally:
        os.chdir( precdir )
        shutil.rmtree(testdir)        


def run(params):
    err=""
    fo,fe = io.StringIO(),io.StringIO()
    with contextlib.redirect_stderr(fe):
        with contextlib.redirect_stdout(fo):
            for err in fakereqman.main(params,avoidBrowser=True):
                if err:
                    break

    output=fo.getvalue()+fe.getvalue()
    print(output)
    return err

