import reqman, asyncio,pytest
from datetime import datetime
from pprint import pprint
import json
s= dict(int=500,str="hello")

MOCK={
    "/a": (200,json.dumps(s)),
    "/b": (200,json.dumps(s)),
}


def test_wait_ok(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
  save:
    time: <<json.int>>

- wait: <<time>>

- GET: /b
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0


def test_wait_ko(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- GET: /a
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
  save:
    time: <<json.int>>

- wait: <<kki>>

- GET: /b
  tests:
    - status: 200
    - json.int: 500
    - json.str: hello
""")

    x=exe(".",fakeServer=MOCK)
    assert "WARNING" in x.console
    assert "can't" in x.console
    assert "wait" in x.console
    assert x.rc == 0


def test_wait_time(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- wait: 200

- GET: /a
  tests:
    - status: 200
""")

    t1 = datetime.now()
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    t2 = datetime.now()

    elapsed = (t2 - t1).total_seconds()
    assert 0.2 <= elapsed < 0.3



def test_wait_time_in_proc(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- proc:
  - wait: 200

  - GET: /a
    tests:
      - status: 200

- call: proc
""")

    t1 = datetime.now()
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    t2 = datetime.now()

    elapsed = (t2 - t1).total_seconds()
    assert 0.2 <= elapsed < 0.3

def test_wait_time_in_proc_proc(exe):

    with open("f1.yml","w+") as fid:
        fid.write("""
- proc2:
    - wait: 200

- proc:
  - call: proc2

  - wait: 200

  - GET: /a
    tests:
      - status: 200

- call: proc
""")

    t1 = datetime.now()
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    t2 = datetime.now()

    elapsed = (t2 - t1).total_seconds()
    assert 0.4 <= elapsed < 0.5



def test_wait_time_rconf(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
proc:
  - wait: 200

  - GET: /a
    tests:
      - status: 200
""")

    with open("f1.yml","w+") as fid:
        fid.write("""
- call: proc
""")

    t1 = datetime.now()
    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0
    t2 = datetime.now()

    elapsed = (t2 - t1).total_seconds()
    assert 0.2 <= elapsed < 0.3