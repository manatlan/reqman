import pytest,json
import newcore.env
import newcore.com


def test_simul_json():
    env=newcore.env.Env(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    obj= dict(items=list("abc"),value="hello")

    tests=[
        ("status","<<v200>>"),
        ("status",".>= <<v200>>"),
        ("status",".> 100"),
        ("response.status",200),
        ("json.items.size",".> 2"),
        ("json.value|upper","HELLO"),
        ("response.json.items.size",3),
        ("rm.response.json.items.size",3),
        ("request.method","GET"),
        ("rm.request.method|upper","GET"),
        ("response.headers.x-test","hello"),
        ("rm.response.headers.X-TeSt|upper","HELLO"),
        ("unknwon|upper",None),
        ("response.json", json.dumps(obj)),         # Prob sur "auto_check_values.yml" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ("response.json", obj),
    ]
    saves=[
        ("hello","<<status>>"),
        ("js","<<response.json>>"),
        ("ll","<<response.json.items>>"),
        ("val","<<response.json.items.1>>"),
        ("MAX","<<response.json.value|upper>>"),
        ("nimp","<<nimp>>"),
    ]

    ex=newcore.env.Exchange("GET","/", tests=tests, saves=saves)

    r=newcore.com.Response(200,{"x-test":"hello"},json.dumps(obj).encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex

    assert ex.saves == {'MAX': 'HELLO',
 'hello': '200',
 'js': "{'items': ['a', 'b', 'c'], 'value': 'hello'}",
 'll': "['a', 'b', 'c']",
 'nimp': '<<nimp>>',
 'val': 'b'}

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)



def test_simul_plaintext():
    env=newcore.env.Env(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    tests=[
        ("status","200"),
        ("content",".? O"),
        ("content","OK"),
    ]
    saves=[]

    ex=newcore.env.Exchange("GET","/", tests=tests, saves=saves)

    r=newcore.com.Response(200,{"x-test":"hello"},"OK".encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex.tests


    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)


def test_save_and_test():
    env=newcore.env.Env(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
        justTrue=lambda x,Env: True,
    ))

    tests=[
        ("status","<<v200>>"),
        ("var","ok"),
        ("var","<<var>>"),
        ("var|upper","OK"),
        ("justTrue","true"),    # \__ same !
        ("justTrue","True"),    # /
    ]
    saves=[
        ("var","ok"),
    ]

    ex=newcore.env.Exchange("GET","/", tests=tests, saves=saves)

    obj= dict(items=list("abc"),value="hello")
    r=newcore.com.Response(200,{"x-test":"hello"},json.dumps(obj).encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert ex.saves == {'var': 'ok'}
    assert all(ex.tests),ex.tests

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)
