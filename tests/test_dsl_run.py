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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 1
    assert ll[0].doc=="\n".join(["first","second"])

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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 1
    assert len(ll[0].tests) == 4 #[('t1', 1), ('t2',1), ('t3',1), ('t4', 1)]
    assert all([not i for i in ll[0].tests])

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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 1
    assert ll[0].inHeaders==dict([('x-h1', 'hello1'), ('x-h2', 'hello2')])

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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 1
    assert ll[0]["SCOPE"]=={'p1': 'hello1', 'p2': 'hello2'}

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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 1
    assert ll[0]["SCOPE"]=={'p1': 'hello1', 'p2': 'hello2'}


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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 2
    assert ll[0]["SCOPE"]=={'p1': 'hello1', 'p21': 'hello21'}
    assert ll[1]["SCOPE"]=={'p1': 'hello1', 'p22': 'hello22'}

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
    ll=dsl.FakeExecute( dsl.compile( yaml.load(y) ) )
    assert len(ll) == 2
    assert ll[0]["SCOPE"]=={'p21': 'p21', 'p':'pp','q':'q'}
    assert ll[1]["SCOPE"]=={'p22': 'p22', 'p':'pp','q':'q'}



F=os.path.join(os.path.dirname(os.path.dirname(__file__)),"REALTESTS")
@pytest.mark.parametrize('file', [i[len(F)+1:] for i in glob( os.path.join( F,"auto_*.yml")) + glob( os.path.join( F,"auto_*/*.yml")) if "_ERROR_" not in i] )
def test_file(file):
    dsl.FakeExecute( dsl.compile( yaml.load(FString(os.path.join(F,file))) ) )
