import sys,os,io,contextlib
if __name__=="__main__":
    sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
    import fakereqman,reqman
else:
    import fakereqman,reqman

from glob import glob



def run(params):
    sys.argv=params
    print("\n"+">"*80)
    print(">"," ".join(sys.argv))
    print(">"*80)

    fo,fe = io.StringIO(),io.StringIO()
    with contextlib.redirect_stderr(fe):
        with contextlib.redirect_stdout(fo):
            err=fakereqman.main(runServer=False)
    print(err or "ok")

    output=fo.getvalue()+fe.getvalue()
    return err

def test_autos():
    """
    Will automatically run reqman'tests (auto*.yml) in current folder
    and check if valid according shebang's valid statements
    """
    ll=glob("REALTESTS/auto_*.yml")
    assert ll

    ws=fakereqman.FakeWebServer(11111)
    ws.start()
    import time
    time.sleep(1)   

    try:  
        for f in ll:
            txt=reqman.FString(f)
            firstLine=txt.splitlines()[0]
            
            # get args from the shebang on the yaml
            cmd,params=(firstLine.split("reqman.py"))
            args=params.strip().split(" ")

            # remove "--b" to avoid opening tabs
            if "--b" in args:
                args.remove("--b")

            # and do the tests with optionnal "valid:x:x:x"
            err=run(["FAKEREQMAN",f] + args)
            assert err=="", "File '%s' : %s" % (f,err)

            err=run(["FAKEREQMAN",f] + args + ["--o"])
            assert err=="", "File '%s' : %s" % (f,err)
    finally:
        ws.stop()

if __name__=="__main__":
    test_autos()