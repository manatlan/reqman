import reqman,pytest,sys

def test_COMMAND_no_args(exe):
    r=exe()
    assert r.rc==-1
    assert "ERROR COMMAND: no yml files found" in r.console
    assert "USAGE" in r.console

def test_COMMAND_bad_option(exe):
    r=exe(".","--dsqdqs")
    assert r.rc==-1
    assert "ERROR COMMAND: bad option" in r.console
    assert "USAGE" in r.console

def test_COMMAND_bad_option2(exe):
    r=exe(".","--ko","--jkjkj")
    assert r.rc==-1
    assert "ERROR COMMAND: bad option" in r.console
    assert "USAGE" in r.console

def test_COMMAND_bad_option_try_help(exe):
    r=exe(".","--help")
    # r.view()
    assert r.rc==-1
    assert "ERROR COMMAND: bad option" in r.console
    assert "USAGE" in r.console

def test_EXECUTION_unknown_file(exe):
    r=exe("fdsfdsqgfds")
    assert r.rc==-1
    assert "ERROR EXECUTION: bad param" in r.console
    assert "USAGE" not in r.console

def test_EXECUTION_bad_switch(exe):
    with open("test.yml","w+") as fid:
        fid.write("")
    r=exe(".","-unknown")
    assert r.rc==-1
    assert "ERROR COMMAND: bad switch" in r.console
    assert "USAGE" in r.console



