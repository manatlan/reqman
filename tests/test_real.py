from context import reqman
import os

def test_jsonstore():
    yml=os.path.join(os.path.dirname(__file__),"real/jsonstore.yml")
    x=reqman.main([yml])
    assert x==0

def test_down():
    yml=os.path.join(os.path.dirname(__file__),"real/server_down.yml")
    x=reqman.main([yml])
    assert x==2 # 2 test failed

def test_timeout():
    yml=os.path.join(os.path.dirname(__file__),"real/server_timeout.yml")
    x=reqman.main([yml])
    assert x==2 # 2 test failed