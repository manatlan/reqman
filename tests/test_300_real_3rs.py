import reqman, asyncio,pytest

# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!
# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!
# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!
# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!
# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!
# THESES TESTS CAN ONLY WORK WITH A REAL ACCESS TO FULLY INTERNET !!!

def test_json():
    r=reqman.ReqmanCommand( r"examples/j*" )
    rr=r.execute( )
    # with open("/home/manatlan/aeff1.html","w+") as fid:
    #     fid.write( rr.html )
    assert rr.code==0
    assert rr.nbReqs==7


def test_down():
    r=reqman.ReqmanCommand( r"examples/server_do*" )
    rr=r.execute( )
    # with open("/home/manatlan/aeff2.html","w+") as fid:
    #     fid.write( rr.html )
    assert rr.code==4
    assert rr.nbReqs==2

def test_timeout():
    r=reqman.ReqmanCommand( r"examples/server_ti*" )
    rr=r.execute( )
    # with open("/home/manatlan/aeff3.html","w+") as fid:
    #     fid.write( rr.html )
    assert rr.code==2
    assert rr.nbReqs==1
