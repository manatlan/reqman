import reqman,pytest,sys

def test_COMMAND_bad(exe):
    x=exe("new","gfdfds")
    assert x.rc==-1
    assert "you shoul provide a full url" in x.console


def test_COMMAND_new(exe):
    x=exe("new","http://jim/jo1")
    assert x.rc==0
    assert "Create reqman.conf" in x.console
    assert "Create 0010_test.rml" in x.console

    assert "GET: /jo1" in open("0010_test.rml").read()
    assert "root: http://jim" in open("reqman.conf").read()

    x=exe("new","http://jim/jo2?kif=1")
    assert "Use 'reqman.conf" in x.console
    assert "Create 0020_test.rml" in x.console
    assert "GET: /jo2?kif=1" in open("0020_test.rml").read()

    x=exe("new","/jo3")
    assert "Use 'reqman.conf" in x.console
    assert "Create 0030_test.rml" in x.console
    assert "GET: /jo3" in open("0030_test.rml").read()
    
