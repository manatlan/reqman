from reqman import json,Env


def test_1priority_params_for_proc(exe):
    MOCK={
        "/a":(200,"ok"),
        "/b":(201,"ok"),
    }

    y="""
    - proc:
        - GET: /<<p>>
          params:
            p: a

    - call: proc
      params:
        p: z
      tests:  # "/a" (local "p" is prefered over others)
        - status: 200
        - content: ok
    """

    with open("f.yml", "w+") as fid:
        fid.write(y)

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0



def test_ignorable_params_for_proc(exe): # hey pato, look here
    MOCK={
        "/a":(200,"ok"),
        "/b":(201,"ok"),
    }

    y="""
    - proc:
        - GET: /<<p?|defaulting>>
          params:
            defaulting: return x or "a"

    - call: proc
      params:
        p: b
      tests:            # should be "/b"
        - status: 201
        - content: ok

    - call: proc
      tests:            # should be "/a" (the default)
        - status: 200
        - content: ok
    """

    with open("f.yml", "w+") as fid:
        fid.write(y)

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0



def test_priority_over_env(Reqs):
    y="""
    - GET: /<<var>>
      tests:
        status: 200

    - GET: /<<var>>
      tests:
        status: 201
      params:
        var: second   # override current 'var'

    - GET: /<<var>>
      tests:
        status: 200

    """
    MOCK={
        "/first":(200,'ok'),
        "/second":(201,'ok'),
    }
    ll=Reqs(y,{"var":"first"}).execute(MOCK)
    for i in ll:
      assert all(i.tests)



def test_priority_over_saved(Reqs):
    y="""

    - GET: /first
      tests:
        status: 200
        json.val: bad
      save:
        var: <<json.val>>

    - GET: /<<var>>
      tests:
        status: 404

    - GET: /<<var>>
      tests:
        status: 200
      params:
        var: second   # override current 'var'

    - GET: /<<var>>
      tests:
        status: 404

    """
    MOCK={
        "/first":(200,json.dumps( {"val":"bad"} )),
        "/second":(200,"ok"),
    }
    ll=Reqs(y).execute(MOCK)
    for i in ll:
      assert all(i.tests)

