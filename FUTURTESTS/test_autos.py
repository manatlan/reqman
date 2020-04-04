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

@pytest.mark.parametrize('file', glob("FUTURTESTS/auto_*.yml") )
def test_file(file):
    txt=reqman.FString(file)
    firstLine=txt.splitlines()[0]
    
    # get args from the shebang on the yaml
    cmd,params=(firstLine.split("reqman.py"))
    args=params.strip().split(" ")

    # remove "--b" to avoid opening tabs
    if "--b" in args: args.remove("--b")

    # and do the tests with optionnal "valid:x:x:x"
    err=run(["FAKEREQMAN",file] + args)
    assert err=="", "File '%s' : %s" % (file,err)

    err=run(["FAKEREQMAN",file] + args + ["--o"])
    assert err=="", "File '%s' : %s" % (file,err)    


def run(params):
    sys.argv=params

    fo,fe = io.StringIO(),io.StringIO()
    with contextlib.redirect_stderr(fe):
        with contextlib.redirect_stdout(fo):
            err=fakereqman.main(runServer=False)
    print(">"," ".join(sys.argv),"--->",err or "ok")

    output=fo.getvalue()+fe.getvalue()
    return err


