import reqman, asyncio,pytest
from pprint import pprint
import json


MOCK={
    "/test": (200,"ok"),
}

def test_bad(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("toto: xxx")

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x",fakeServer=MOCK)
    assert x.rc==-1


def test_simplest(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("toto: xxx")

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x:toto",fakeServer=MOCK)
    assert x.rc == 'xxx'


def test_unknown(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("toto: xxx")

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x:unknown",fakeServer=MOCK)
    assert x.rc == None


def test_data(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""toto:
        - 42
        - hello
        """)

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x:toto",fakeServer=MOCK)
    assert x.rc == json.dumps([42,"hello"])

def test_py(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""toto: |
        return 33+11""")

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x:toto",fakeServer=MOCK)
    assert x.rc == 44


def test_py2(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        trans: |
          return x+"lo"
        val: hel

        toto: <<val|trans>>
        """)

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /test
  tests:
    - status: 200
""")

    x=exe(".","--x:toto",fakeServer=MOCK)
    assert x.rc == 'hello'


def test_without_yml(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""toto: hell""")

    x=exe(".","--x:toto",fakeServer=MOCK)
    assert x.rc == -1


def test_without_yml_but_rmconf(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        toto: hello
        tata: |
          return 42

        upper: |
          return x.upper()
        titi: <<toto|upper>>
        """)

    x=exe("reqman.conf","--x:toto",fakeServer=MOCK)
    assert x.rc == 'hello'
    x=exe("reqman.conf","--x:tata",fakeServer=MOCK)
    assert x.rc == 42
    x=exe("reqman.conf","--x:titi",fakeServer=MOCK)
    assert x.rc == 'HELLO'

def test_without_yml_but_rmconf_begin(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        BEGIN:
            - GET: /test
              tests:
                - status: 200
              save: toto        #save content od '/test' in var 'toto'

        """)

    x=exe("reqman.conf","--x:toto",fakeServer=MOCK)
    assert x.rc == 'ok'

def test_without_yml_but_rmconf_begin2(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        BEGIN:
            - GET: /test
              tests:
                - status: 200
              save:
                titi: 42
                toto: <<content|upper>>
              params:
                upper: |
                    return x.decode().upper()

        """)

    x=exe("reqman.conf","--x:titi",fakeServer=MOCK)
    assert x.rc == 42
    x=exe("reqman.conf","--x:toto",fakeServer=MOCK)
    assert x.rc == 'OK'


def test_without_yml_but_rmconf_begin_bytes(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        BEGIN:
            - GET: /test
              tests:
                - status: 200
              save:
                toto: <<content|upper>>
              params:
                upper: |
                    return x.upper()    #bytes

        """)

    x=exe("reqman.conf","--x:toto",fakeServer=MOCK)
    assert x.rc == b"OK"    # keep bytes


def test_a_trans_from_input(exe):
    with open("reqman.conf","w+") as fid:
        fid.write("""
        in: default
        upper: |
          return x.upper()
        out: <<in|upper>>
        """)

    x=exe("reqman.conf","--x:out",fakeServer=MOCK)
    assert x.rc == 'DEFAULT'
    x=exe("reqman.conf","in:hello","--x:out",fakeServer=MOCK)
    assert x.rc == 'HELLO'


def test_a_trans_from_input_with_exposed_one(exe):

    def func(x,ENV):
        return x.upper()

    reqman.EXPOSEDS={
        "UPPER": func
    }

    with open("reqman.conf","w+") as fid:
        fid.write("""
        in: default
        out: <<in|UPPER>>
        """)

    x=exe("reqman.conf","--x:out",fakeServer=MOCK)
    assert x.rc == 'DEFAULT'
    x=exe("reqman.conf","in:hello","--x:out",fakeServer=MOCK)
    assert x.rc == 'HELLO'
