import reqman,pytest,sys,os


def test_COMMAND_usage_no_files(exe):
    x=exe(".")
    assert "ERROR COMMAND: no yml files found" in x.console
    assert "USAGE" in x.console
    assert "pre-made 'switch' defined" in x.console
        
def test_COMMAND_usage_list_switches(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("root: 'https://s1.com'\n")
        fid.write("sw1:\n")
        fid.write("    root: 'https://s2.com'\n")
        
    x=exe(".")
    assert "Use 'reqman.conf" in x.console
    assert "ERROR COMMAND: no yml files found" in x.console
    assert "USAGE" in x.console
    assert "-sw1 :" in x.console

