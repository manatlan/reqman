import pytest
import newcore.utils


def test_comp():
    compare=lambda x,opeval: newcore.utils.testCompare("my",x,opeval)

    assert compare(201,"201")
    assert compare(201,".= 201")
    assert compare(201,".== 201")
    assert compare(201,".> 200")
    assert compare("201",".> 200")
    assert compare("200",".>= 200")
    assert compare("200",".<= 200")
    assert compare("200",".< 201")
    assert compare("200",".!= 201")
    assert compare("200",".!== 201")

    assert compare("ABC",".? A")
    assert compare("ABC",".!? Z")
