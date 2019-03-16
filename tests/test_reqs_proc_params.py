from context import reqs,reqman
import json,pytest
SERVER={"/": (200,"hello")}


def test_yml_procedures_call_with_diff_types(reqs):

    y="""
- jo:
      POST: /
      body:
        <<val>>

- call: jo
  params:
    val:
        - 1
        - 2

- call: jo
  params:
    val:
        a: 1
        b: 2

"""
    l=reqs(y)
    assert len(l), 2

    r=l[0].test({})
    assert json.loads(r.req.body), [1,2] 

    r=l[1].test({})
    assert json.loads(r.req.body), dict(a=1,b=2) 

def test_yml_procedures_call_with_sub_diff_types(reqs):

    y="""
- jo:
      POST: /
      body:
        data:
            "{{val}}"

- jack:
      POST: /
      body:
        data:
            <<val>>         # second escaper

- call: jo
  params:
    val:
        - 1
        - 2

- call: jo
  params:
    val:
        a: 1
        b: 2

- call: jack
  params:
    val:
        - 1
        - 2

- call: jack
  params:
    val:
        a: 1
        b: 2

"""
    l=reqs(y)
    assert len(l)== 4

    r=l[0].test({})
    assert json.loads(r.req.body) == {'data': [1, 2]} 

    r=l[1].test({})
    assert json.loads(r.req.body) ==  {'data': dict(a=1,b=2) } 

    r=l[2].test({})
    assert json.loads(r.req.body) == {'data': [1, 2]} 

    r=l[3].test({})
    assert json.loads(r.req.body) ==  {'data': dict(a=1,b=2) } 


def test_yml_procedures(reqs):

    y="""
- jo:
    GET: /
- call: jo
- call: jo
- call: jo
- {"call": "jo"}    #json notation (coz json is a subset of yaml ;-)
"""
    l=reqs(y)
    assert len(l)== 4


def test_yml_procedures_multiple(reqs):     # NEW
    y="""
- jo:
    - GET: /
    - POST: /
    - PUT: /
- call: jo
"""
    l=reqs(y)
    assert len(l) == 3

    y="""
- jo:
    - GET: /
    - POST: /
    - PUT: /
- call: jo
- call: jo
"""
    l=reqs(y)
    assert len(l) == 6

def test_yml_call_procedures_as_list(reqs):
    y="""
- jo:
    - GET: /
    - POST: /
    - PUT: /
- call:
    - jo
    - jo
"""
    l=reqs(y)
    assert len(l) == 6



def test_yml_procedures_multiple_mad(reqs):     # NEW
    y="""
- jo:
    - jack:
        GET: /

    - call: jack
    - call: jack
- call: jo
"""
    l=reqs(y)
    assert len(l)== 2


def test_yml_procedures_def_without_call(reqs):

    y="""
- jo:
    GET: /
"""
    l=reqs(y)
    assert len(l)== 0    # 0 request !

def test_yml_procedures_call_without_def(reqs):

    y="""
- call: me
"""
    with pytest.raises(reqman.RMException):
        reqs(y)


def test_yml_procedure_global(reqs):     # NEW
    y="""
- call: me
"""
    env={
        "me": [{"GET":"/"},{"POST":"/"}],   # declare a global proc
    }

    l=reqs(y,env)
    assert len(l)== 2


