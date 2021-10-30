import pytest
import reqman.dsl as dsl
from reqman.common import FString

import yaml
from glob import glob
import os

def test_call_with_doc():
    y="""
- proc:
    GET: yolo
    doc: first
- call: proc
  doc: second
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 1
    assert ll[0]["OP"]=="HTTP"
    assert ll[0]["doc"]==["first","second"]

def test_call_with_tests():
    y="""
- proc:
    GET: yolo
    tests:
        - t1: 1
        - t2: 1
- call: proc
  tests:
    t3: 1
    t4: 1
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 1
    assert ll[0]["OP"]=="HTTP"
    assert ll[0]["tests"]==[('t1', 1), ('t2',1), ('t3',1), ('t4', 1)]

def test_call_with_headers():
    y="""
- proc:
    GET: yolo
    headers:
        x-h1: hello1
- call: proc
  headers:
    - x-h2: hello2
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 1
    assert ll[0]["OP"]=="HTTP"
    assert ll[0]["headers"]==[('x-h1', 'hello1'), ('x-h2', 'hello2')]

def test_call_with_params():
    y="""
- proc:
    GET: yolo
    params:
      p1: hello1
- call: proc
  params:
    p2: hello2
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 1
    assert ll[0]["OP"]=="HTTP"
    assert ll[0]["scope"]=={'p1': 'hello1', 'p2': 'hello2'}

def test_call_with_params2():
    y="""
- proc:
    GET: yolo
    params:
      p1: hello1
- call: proc
  params:
    - p2: hello2
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 1
    assert ll[0]["OP"]=="HTTP"
    assert ll[0]["scope"]=={'p1': 'hello1', 'p2': 'hello2'}


def test_call_with_params3():
    y="""
- proc:
    GET: yolo
    params:
      p1: hello1
- call: proc
  params:
    - p21: hello21
    - p22: hello22
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 2
    assert ll[0]["OP"]=="HTTP"
    assert ll[1]["OP"]=="HTTP"
    assert ll[0]["scope"]=={'p1': 'hello1', 'p21': 'hello21'}
    assert ll[1]["scope"]=={'p1': 'hello1', 'p22': 'hello22'}

def test_call_with_foreach_and_params():
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
    p: p
    q: q
"""
    ll=list(dsl.execute( dsl.compile( yaml.load(y) ) ))
    assert len(ll) == 2
    assert ll[0]["OP"]=="HTTP"
    assert ll[1]["OP"]=="HTTP"
    assert ll[0]["scope"]=={'p21': 'p21', 'p':'pp','q':'q'}
    assert ll[1]["scope"]=={'p22': 'p22', 'p':'pp','q':'q'}



F=os.path.join(os.path.dirname(os.path.dirname(__file__)),"REALTESTS")
@pytest.mark.parametrize('file', [i[len(F)+1:] for i in glob( os.path.join( F,"auto_*.yml")) + glob( os.path.join( F,"auto_*/*.yml")) if "_ERROR_" not in i] )
def test_file(file):
    dsl.execute( dsl.compile( yaml.load(FString(os.path.join(F,file))) ) )