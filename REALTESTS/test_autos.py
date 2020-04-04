import sys,os,io,contextlib
from glob import glob
import pytest
import fakereqman, reqman

ws=None
def setup_module():
    global ws
    ws=fakereqman.FakeWebServer(11111)
    ws.start()
    import time
    time.sleep(1)   

def teardown_module():
    global ws
    ws.stop()

@pytest.mark.parametrize('file', glob("REALTESTS/auto_*.yml") )
def test_file(file):
    err=run(["FAKEREQMAN",file])
    assert err=="", "File '%s' : %s" % (file,err)

def run(params):
    err=""
    fo,fe = io.StringIO(),io.StringIO()
    with contextlib.redirect_stderr(fe):
        with contextlib.redirect_stdout(fo):
            for err in fakereqman.main(params,runServer=False):
                if err:
                    break

    output=fo.getvalue()+fe.getvalue()
    return err

