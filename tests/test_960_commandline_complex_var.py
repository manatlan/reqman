import reqman,pytest,sys,os

def test_COMMAND_complex(exe):   #<- it's not a real test ... just COPY/PASTE this one for next tests
    mock = {"/hello":(200,"ok")}

    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: /<<var.a.b>>
          tests:
            - status: 200
            - content: ok
          params:
            var: |
                d={}
                d["a"]={"b":"hello"}
                return d
        """)
        
    x=exe(".",fakeServer=mock)
    assert os.path.isfile("reqman.html")
    assert x.rc == 0

