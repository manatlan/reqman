import reqman
import fakereqman
import sys,time
from glob import glob

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
            with open(f) as fid:
                firstLine=fid.readline()
            
            # get args from the shebang on the yaml
            cmd,params=(firstLine.split("reqman.py"))
            args=params.strip().split(" ")

            # remove "--b" to avoid opening tabs
            if "--b" in args:
                args.remove("--b")
                args.append("--k")

            # and do the tests with optionnal "valid:x:x:x"
            sys.argv=["FAKEREQMAN",f] + args
            print("\n"+">"*80)
            print(">"," ".join(sys.argv))
            print(">"*80)
            assert fakereqman.main(runServer=False)==0, "File '%s' is not valid" % f
            # sys.argv=["FAKEREQMAN",f] + args + ["--o"]
            # print("\n"+">"*80)
            # print(">"," ".join(sys.argv))
            # print(">"*80)
            # assert fakereqman.main()==0, "File '%s' is not valid" % f
    finally:
        ws.stop()