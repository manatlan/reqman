import reqman, asyncio,pytest
from pprint import pprint
import json


MOCK={
    "/test": (200,"ok"),
}


def test_run_rmconf(exe): # do nothing (except check syntax)
    with open("reqman.conf","w+") as fid:
        fid.write("""
        toto: hello
        """)

    x=exe("reqman.conf",fakeServer=MOCK)
    assert x.rc == 0
