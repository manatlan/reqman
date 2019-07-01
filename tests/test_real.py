import os
import reqman
import asyncio

def test_jsonstore():
    yml=os.path.join(os.path.dirname(__file__),"real/jsonstore.yml")
    rc=asyncio.run(reqman.commandLine([yml]))
    assert rc==0

def test_down():
    yml=os.path.join(os.path.dirname(__file__),"real/server_down.yml")
    rc=asyncio.run(reqman.commandLine([yml]))
    assert "ERROR: Server is down" in rc.details.html
    assert rc==2 # 2 test failed

def test_timeout():
    yml=os.path.join(os.path.dirname(__file__),"real/server_timeout.yml")
    rc=asyncio.run(reqman.commandLine([yml]))
    assert rc==2 # 2 test failed