import pytest, reqman, json
import datetime,pickle


def test_updateUrlQuery():
    u="https://jo.com/me?a=1&a=2&b=hello#anchor"

    assert reqman.updateUrlQuery(u,dict(z=42))=="https://jo.com/me?a=1&a=2&b=hello&z=42#anchor"     # add a var
    assert reqman.updateUrlQuery(u,dict(a=3))=="https://jo.com/me?a=1&a=2&a=3&b=hello#anchor"       # append a value to existing "a"
    assert reqman.updateUrlQuery(u,dict(a=None))=="https://jo.com/me?b=hello#anchor"                # remove completly "a"
    assert reqman.updateUrlQuery(u,dict(a=""))=="https://jo.com/me?a=1&a=2&a=&b=hello#anchor"       # append a value (emptystring) to existing "a"
    assert reqman.updateUrlQuery(u,dict(x=None))==u                                                 # try to remove an unknown one
    assert reqman.updateUrlQuery(u,dict(a="a s"))=="https://jo.com/me?a=1&a=2&a=a+s&b=hello#anchor"    # append a value (a+s) to existing "a"
    assert reqman.updateUrlQuery(u,dict(a=[4,5]))=="https://jo.com/me?a=1&a=2&a=4&a=5&b=hello#anchor"  # append a values to existing "a"
