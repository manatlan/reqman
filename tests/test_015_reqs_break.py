import pytest,reqman


def test_break(Reqs):
    y="""
- GET: https://www.manatlan.com
- break
- GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 1

def test_break_in_proc(Reqs):
    y="""
- Tests:
    - GET: https://www.manatlan.com
    - break
    - GET: https://www.manatlan.com
- call: Tests
- GET: https://www.manatlan.com
"""
    l=Reqs(y)
    assert len(l) == 2
