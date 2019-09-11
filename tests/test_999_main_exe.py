import reqman,pytest,sys,os
import contextlib,io

def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

def test_exe(): #ensure that the module is executable (thru its "if __name__=="__main__":)
    sys.argv=[""]
    fo,fe = io.StringIO(),io.StringIO()
    with pytest.raises(SystemExit):
        with contextlib.redirect_stderr(fe):
            with contextlib.redirect_stdout(fo):
                execfile("reqman.py")
    output=fo.getvalue()+fe.getvalue()      
    assert "USAGE" in output
    assert reqman.__version__ in output

        
