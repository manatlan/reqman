import reqman,pytest,sys,os

def test_COMMAND_complex(exe):   
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
    assert x.rc == 0

def test_COMMAND_complex2(exe):   
    mock = {"/HELLO":(200,"ok")}

    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: /<<var.a.b|upper>>
          tests:
            - status: 200
            - content: ok
          params:
            var: |
                d={}
                d["a"]={"b":"hello"}
                return d
            upper:
              return x.upper()
        """)
        
    x=exe(".",fakeServer=mock)
    assert x.rc == 0

