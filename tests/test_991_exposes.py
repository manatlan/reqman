import pytest,reqman,json

MOCK={
    "/ok":(200,"ok"),
    "/ko":(400,"ko"),
}

def test_simple_ok(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ok" if x["login"]==x["passwd"] else "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<User1|Authent>>
  tests:
    - status: 200
    - content: ok

- GET: /<<User2|Authent>>
  tests:
    - status: 400
    - content: ko
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
User1:
    login:  jo
    passwd: jo

User2:
    login:  jo1
    passwd: jo2
""")


    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0




def test_simple_with_list(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ok" if len(x)==2 else "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj1|Authent>>
  tests:
    - status: 200
    - content: ok

- GET: /<<obj2|Authent>>
  tests:
    - status: 400
    - content: ko
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj1:
    - 12
    - 42
obj2: [1,2,3]
""")


    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0


def test_simple_with_str(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: x
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj1|Authent>>
  tests:
    - status: 200
    - content: ok

- GET: /<<obj2|Authent>>
  tests:
    - status: 400
    - content: ko
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj1: ok
obj2: ko
""")


    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0




def test_bad(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ok" if x["login"]==x["passwd"] else "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj:                                                # too less
    login:  jo
""")

    x=exe(".",fakeServer=MOCK)
    assert x.rc == 2 # 2 ko tests


def test_bug_in_exposedMethod(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: 42/0
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj: OSEF
""")

    x=exe(".",fakeServer=MOCK)
    assert x.rc == 2 # 2 ko tests

def test_ok_with_toomuch(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ok" if x["login"]==x["passwd"] else "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj:                                                 # too much
    login:  jo
    passwd:  jo
    name:  jo
""")

    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0

def test_bad_with_not_awaited_ones(exe): # dict as kargs

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ok" if x["login"]==x["passwd"] else "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
obj:                                                 # not awaited ones
    mylogin:  jo
    mypasswd:  jo
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 2 # 2 ko tests


def test_pymethod_over_exposedMethod(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x, ENV: "ko"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""

Authent:
    return "ok"

obj: OSEF
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0 # the one in rc.conf is prefered over the exposed one

def test_with_ENV(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x,ENV: ENV.get("global","ko")
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok

- GET: /<<obj|Authent>>
  params:
    global: ko              #override global
  tests:
    - status: 400
    - content: ko

- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok

""")

    with open("reqman.conf","w+") as fid:
        fid.write("""

global: ok

obj: OSEF
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0 # the one in rc.conf is prefered over the exposed one

def test_decorator(exe):

    @reqman.expose
    def AnotherAuthent( x, ENV):
        return "ok" if x["login"]==x["passwd"] else "ko"

    assert "AnotherAuthent" in reqman.EXPOSEDS

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<User1|AnotherAuthent>>
  tests:
    - status: 200
    - content: ok

- GET: /<<User2|AnotherAuthent>>
  tests:
    - status: 400
    - content: ko
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""
User1:
    login:  jo
    passwd: jo

User2:
    login:  jo1
    passwd: jo2
""")


    x=exe(".",fakeServer=MOCK)
    assert x.rc == 0

def test_bad_sign(exe):

    reqman.EXPOSEDS={
        "Authent": lambda x: "nothing here, the signature is not callable"
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""

obj: OSEF
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 2 # 2 tests ko


def test_no_input(exe):

    def func(x,ENV):
        return "ok"

    reqman.EXPOSEDS={
        "Authent": func
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""

""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0 # all ok



def test_input_is_json_str(exe):

    def func(x,ENV):
        return x==[1,2,3] and "ok"

    reqman.EXPOSEDS={
        "Authent": func
    }

    with open("f.yml","w+") as fid:
        fid.write("""
- GET: /<<obj|Authent>>
  tests:
    - status: 200
    - content: ok
""")

    with open("reqman.conf","w+") as fid:
        fid.write("""

obj: "[1,2,3]"
""")

    x=exe(".",fakeServer=MOCK)
    # x.view()
    assert x.rc == 0 # all ok
