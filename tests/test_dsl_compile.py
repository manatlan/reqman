import pytest
import reqman.dsl as dsl
from reqman.common import FString

import yaml
from glob import glob
import os

def test_compile_emptys():
    assert dsl.compile( [] ) == []
    assert dsl.compile( {} ) == []

    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( None )

    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( "hello" )

def test_unknown_attr():
    y="""
- GET: yolo
  nimp: toto
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

def test_bad_order():
    y="""
- body: toto
  POST: yolo
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

def test_good_order():
    y="""
- POST: yolo
  body: toto

"""
    assert len(dsl.compile( yaml.load(y) )) == 1

def test_call_bad():
    y="""
- call: unknown
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

    y="""
- proc:
    GET: yolo
- call: 12
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

    y="""
- proc:
    GET: yolo
- call: <<dynamic>>
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

    y="""
- proc:
    GET: yolo
- call:
    - proc
    - <<dynamic>>
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )

    y="""
- proc:
    GET: yolo
- call:
    - proc
    - 12
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )


def test_call_str():
    y="""
- proc:
    GET: yolo
- call: proc
"""
    assert len(dsl.compile( yaml.load(y) )) == 2

def test_call_list():
    y="""
- proc:
    GET: yolo
- call:
    - proc
    - proc
"""
    assert len(dsl.compile( yaml.load(y) )) == 3

def test_call_with_doc():
    y="""
- proc:
    GET: yolo
    doc: first
- call: proc
  doc: second
"""
    ll=dsl.compile( yaml.load(y) )
    assert len(ll) == 2

def test_call_with_tests():
    y="""
- proc:
    GET: yolo
    tests:
        - status: 200
- call: proc
  tests:
    - content: "ok"
"""
    ll=dsl.compile( yaml.load(y) )
    assert len(ll) == 2


def test_call_try_mix_foreach_and_params():
    y="""
- proc:
    GET: yolo
    params:
        p: pp
- call: proc
  foreach:
    - p21: p21
    - p22: p22
  params:
    - p: p
    - q: q
"""
    with pytest.raises(dsl.RMDslCompileException):
        dsl.compile( yaml.load(y) )


F=os.path.join(os.path.dirname(os.path.dirname(__file__)),"REALTESTS")
@pytest.mark.parametrize('file', [i[len(F)+1:] for i in glob( os.path.join( F,"auto_*.yml")) + glob( os.path.join( F,"auto_*/*.yml")) if "_ERROR_" not in i] )
def test_file(file):
    dsl.compile( yaml.load(FString(os.path.join(F,file))) )
