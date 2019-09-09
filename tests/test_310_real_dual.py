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


@pytest.mark.asyncio
async def test_dual():
    r=reqman.ReqmanCommand( r"examples/dual" )
    rr=await r.asyncExecuteDual( [],["site1"] )
    with open("/home/manatlan/aeff.html","w+") as fid:
        fid.write( reqman.render(rr))
