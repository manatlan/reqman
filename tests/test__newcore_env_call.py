import pytest,json
import reqman.env
import reqman.com


def test_simul_json():
    env=reqman.env.Scope(dict(
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

    ex=reqman.env.Exchange("GET","/", tests=tests, saves=saves)

    r=reqman.com.Response(200,{"x-test":"hello"},json.dumps(obj).encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex
    assert ex.saves["hello"]==200
    assert ex.saves["js"]=={"items": ["a", "b", "c"], "value": "hello"}
    assert ex.saves["ll"]==["a", "b", "c"]
    assert ex.saves["val"]=="b"
    assert ex.saves["MAX"]=="HELLO"
    assert ex.saves["nimp"]=="<<nimp>>"

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)



def test_simul_plaintext():
    env=reqman.env.Scope(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    tests=[
        ("status","200"),
        ("content",".? O"),
        ("content","OK"),
    ]
    saves=[]

    ex=reqman.env.Exchange("GET","/", tests=tests, saves=saves)

    r=reqman.com.Response(200,{"x-test":"hello"},"OK".encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex.tests


    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)


def test_save_and_test():
    env=reqman.env.Scope(dict(
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

    ex=reqman.env.Exchange("GET","/", tests=tests, saves=saves)

    obj= dict(items=list("abc"),value="hello")
    r=reqman.com.Response(200,{"x-test":"hello"},json.dumps(obj).encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert ex.saves == {'var': 'ok'}
    assert all(ex.tests),ex.tests

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)




def test_simul_xml():
    env=reqman.env.Scope(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
    ))

    xml= "<a><b>1</b><b>2</b></a>"

    tests=[
        ("status","200"),
        ("content",xml),
        ("xml.//b.0", "1"),
        ("xml.//b", ["1","2"] ),
    ]
    saves=[
        ("toto","<<xml.//b>>")
    ]

    ex=reqman.env.Exchange("GET","/", tests=tests, saves=saves)

    r=reqman.com.Response(200,{"x-test":"hello"},xml.encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex

    assert ex.saves["toto"]== ["1", "2"]

    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)


def test_simul_bytes():
    env=reqman.env.Scope(dict(
        v200=200,
        upper= lambda x,ENV: x.upper(),
        mkbytes=lambda x,ENV: b"[1234]",
    ))

    tests=[
        # ("status","200"),
        # ("content",".? [1234]"),
        ("content",".? <<mkbytes>>"),
    ]
    saves=[]

    ex=reqman.env.Exchange("GET","/", tests=tests, saves=saves)

    content="".join([f"[{i}]" for i in range(10000)])
    r=reqman.com.Response(200,{"x-test":"hello"},content.encode(),"http1/1 200 ok")
    ex.treatment(env,r)

    assert ex.time==0
    assert ex.id

    assert all(ex.tests),ex.tests


    import pprint
    pprint.pprint(ex.tests)
    pprint.pprint(ex.saves)
