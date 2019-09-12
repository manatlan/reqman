import pytest,reqman,json

MOCK={
    "https://www.manatlan.com/utf8":(200,"oké"),
    "https://www.manatlan.com/cp1252":(200,"oké".encode().decode("cp1252")),
}

def test_same_encoding(Reqs):
    y="""
GET: https://www.manatlan.com/utf8
tests:
    - content: oké
"""
    l=Reqs(y)
    assert len(l) == 1
    ll= l.execute(MOCK)
    assert any(ll[0].tests)

def test_same_encoding2(Reqs):
    y="""
GET: https://www.manatlan.com/cp1252
tests:
    - content: oké
""".encode().decode("cp1252")
    l=Reqs(y)
    assert len(l) == 1
    ll= l.execute(MOCK)
    assert any(ll[0].tests)

def test_diff_encoding(Reqs):
    y="""
GET: https://www.manatlan.com/cp1252
tests:
    - content: oké
"""
    l=Reqs(y)
    assert len(l) == 1
    ll= l.execute(MOCK)
    assert any(ll[0].tests) #can't resolve ;-( (NEXT UPDATE !!! it's in the pipe)
