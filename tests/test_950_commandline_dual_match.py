import reqman, asyncio,pytest
from pprint import pprint

# def test_solo1():
#     r=reqman.ReqmanCommand( r"examples/dual" )
#     rr=r.execute( )
#     with open("/home/manatlan/aeff1.html","w+") as fid:
#         fid.write( reqman.render(rr))

# def test_solo2():
#     r=reqman.ReqmanCommand( r"examples/dual" )
#     rr=r.execute( ["site1"] )
#     with open("/home/manatlan/aeff2.html","w+") as fid:
#         fid.write( reqman.render(rr))


# @pytest.mark.asyncio
# async def test_dual():
#     r=reqman.ReqmanCommand( r"examples/dual" )
#     rr=await r.asyncExecuteDual( [],["site1"] )
#     with open("/home/manatlan/aeff.html","w+") as fid:
#         fid.write( reqman.render(rr))

MOCK={
    "http://a/1":(200,"ok"),
    "http://a/2":(200,"ok"),
    "http://a/3":(200,"ok"),
    "http://b/1":(201,"ok"),
    "http://b/2":(201,"ok"),
    "http://b/3":(201,"ok"),
}

def test_dual_izip(exe):  

    with open("reqman.conf","w+") as fid:
        fid.write("""
        root: http://a
        def: A

        switches:
          other:
            root: http://b
            def: B
        """)

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<i>>
  doc: "call <<i>>"
  foreach:
    - i: 1
    - i: 2
    - i: 3
  tests:
    - content: ok

""")
        
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0

    x=exe(".","+other",fakeServer=MOCK)
    assert x.rc == 0
    # x.view()
