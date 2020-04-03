import reqman,pytest,sys,os

def test_COMMAND_output_reqman_html(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: http://localhost:8080/
        """)
    assert not os.path.isfile("reqman.html")
        
    x=exe(".")

    assert os.path.isfile("reqman.html")

def test_COMMAND_no_output_html(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: http://localhost:8080/
        """)
    assert not os.path.isfile("reqman.html")
    x=exe(".","--o")
    assert "---------------------------------------------------------------------------" in x.console # ensure display FULL HTTP TRACE in console
    assert not os.path.isfile("reqman.html")

def test_COMMAND_output_anotherFile(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: http://localhost:8080/
        """)
    assert not os.path.isfile("reqman.html")
    x=exe(".","--o:kiki.html")
    assert not os.path.isfile("reqman.html")
    assert os.path.isfile("kiki.html")

def test_COMMAND_only_ko(exe):
    mock = {"/hello":(200,"ok")}

    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: /hello
          tests:
            - status: 200
            - content: ok
        """)
        
    x=exe(".","--k",fakeServer=mock)
    assert x.rc == 0
    assert x.console.strip().startswith("RESULT:")  # there is no KO, no output (except result: %d/%d)

    x=exe(".",fakeServer=mock)
    assert x.rc == 0
    assert not x.console.strip().startswith("RESULT:")  # there is no KO, but output (minimal one) !!
    assert "TEST:" in x.console



def test_COMMAND_shebang(exe):   #<- it's not a real test ... just COPY/PASTE this one for later tests
    mock = {"/hello":(200,"ok")}

    with open("f.yml","w+") as fid:
        fid.write("""#! --k
        - GET: /hello
          tests:
            - status: 200
            - content: ok
        """)
        
    x=exe("--i","f.yml",fakeServer=mock) # should call A file only !
    assert os.path.isfile("reqman.html")
    assert x.rc == 0
    assert "Use SHEBANG : " in x.console
    assert "TEST:" not in x.console # ensure no test are displayed (--ko)


def test_COMMAND_fakeServer(exe):   #<- it's not a real test ... just COPY/PASTE this one for next tests
    mock = {"/hello":(200,"ok")}

    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: /hello
          tests:
            - status: 200
            - content: ok
        """)
        
    x=exe(".",fakeServer=mock)
    assert os.path.isfile("reqman.html")
    assert x.rc == 0

