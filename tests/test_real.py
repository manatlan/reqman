import os
import reqman

def test_jsonstore():
    yml=os.path.join(os.path.dirname(__file__),"real/jsonstore.yml")
    x=reqman.main([yml])
    assert x.code==0

def test_down():
    yml=os.path.join(os.path.dirname(__file__),"real/server_down.yml")
    x=reqman.main([yml])
    assert x.code==2 # 2 test failed

def test_timeout():
    yml=os.path.join(os.path.dirname(__file__),"real/server_timeout.yml")
    x=reqman.main([yml])
    assert x.code==2 # 2 test failed