import reqman,pytest,sys,os

mock = {
  "http://a/start":(200,"ok"),
  "http://b/start":(200,"ok"),
  "http://a/hello":(200,"ok"),
  "http://b/hello":(200,"ok"),
}

def _continue(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: /hello
          doc: ici <<def>>
          tests:
            - status: 200
            - content: ok
        """)
        
    x=exe(".","--s",fakeServer=mock)  # generate a RMR
    assert "http://a/hello" in x.console
    assert x.rc==0
    assert x.console.count("content contains")==1
    assert os.path.isfile("reqman.html")
    os.unlink("reqman.html")
    lrmr=[i for i in os.listdir(".") if i.endswith(".rmr")]
    assert len(lrmr)==1
    os.unlink("reqman.conf")
    os.unlink("f.yml")
    # x.view()


    x=exe(lrmr[0],"--o:r1.html",fakeServer=mock) # rebuild HTML from a rmr -> single result
    assert "http://a/hello" not in x.console # because nothing is replayed
    assert x.rc==0
    assert os.path.isfile("r1.html")
    assert not x.console.count("content contains")==1 # nothing is replayed, only output

    x=exe(lrmr[0],"-other","--o:r2.html",fakeServer=mock) # replay RMR with another switch  -> single result
    assert "http://b/hello" in x.console
    assert "http://a/hello" not in x.console
    assert x.rc==0
    assert os.path.isfile("r2.html")
    assert x.console.count("content contains")==2

    x=exe(lrmr[0],"+other","--o:r3.html",fakeServer=mock) # compare RMR with another switch  -> dual result
    assert "http://b/hello" in x.console
    assert "http://a/hello" not in x.console #because A is not replayed
    assert x.rc==0
    assert os.path.isfile("r3.html")
    assert x.console.count("content contains")==2

    x=exe(lrmr[0],"--r","--o:r4.html",fakeServer=mock) # REPLAY the RMR, and compare old and new -> dual
    assert "http://b/hello" not in x.console
    assert "http://a/hello" in x.console
    assert x.rc==0
    assert os.path.isfile("r4.html")
    assert x.console.count("content contains")==1
    # x.view()

def test_COMMAND_rmr_tests_old_switches(exe):   #<- it's not a real test ... just COPY/PASTE this one for next tests

    with open("reqman.conf","w+") as fid:
        fid.write("""
        root: http://a
        def: A

        other:
          root: http://b
          def: B

          BEGIN:
          - GET: /start
            doc: ici <<def>>
            tests:
              - status: 200
              - content: ok

        """)
    _continue(exe)

def test_COMMAND_rmr_tests_new_switches(exe):   #<- it's not a real test ... just COPY/PASTE this one for next tests

    with open("reqman.conf","w+") as fid:
        fid.write("""
        root: http://a
        def: A

        switches:
          other:
            root: http://b
            def: B

            BEGIN:
            - GET: /start
              doc: ici <<def>>
              tests:
                - status: 200
                - content: ok
        """)
    _continue(exe)
