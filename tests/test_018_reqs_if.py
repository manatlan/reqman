from src import reqman
import pytest


def test_if_ok(Reqs):
    y="""
- if: true
  GET: https://www.manatlan.com

- if: false
  GET: https://www.manatlan.com

- if: 1
  GET: https://www.manatlan.com

- if: 0
  GET: https://www.manatlan.com

- if: <<var>>
  GET: https://www.manatlan.com

- if: null                        # always false
  GET: https://www.manatlan.com

- if: gfdgsfd                     # always true
  GET: https://www.manatlan.com

"""
    l=Reqs(y)
    assert len(l) == 7



def test_if_list_ko(Reqs):
    y="""
- if:
    - <<var1>>
    - <<var2>>
  GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)


def test_if_dict_ko(Reqs):
    y="""
- if:
    a: b
    c: d
  GET: https://www.manatlan.com
"""
    with pytest.raises(reqman.RMFormatException):
        Reqs(y)

