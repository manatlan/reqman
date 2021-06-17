import pytest,reqman


def test_wait_ok(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: 0
- wait: 1000
- wait: 1.1
- wait: 1e3
- wait: <<var>>
- wait: <<var|func>>
- GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 8

def test_wait_ko_string(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: helloWorld
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)


def test_wait_ko_bool(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: true
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_wait_ko_list(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: [1,2]
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

def test_wait_ko_dict(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait:
    a: 1
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)



def test_wait_ko_null(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: null
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)


def test_wait_ko_badFloat(Reqs):
    y="""
- GET: https://www.manatlan.com
- wait: 1,1
- GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

