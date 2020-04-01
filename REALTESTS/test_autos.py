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
        sys.argv=["test",f] + args
        print(sys.argv)
        assert fakereqman.main()==0, "File '%s' is not valid" % f
