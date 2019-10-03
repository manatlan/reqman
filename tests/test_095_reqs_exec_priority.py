from reqman import json,Env


def test_priority_dont_override_local_value(Reqs):
    MOCK={
        "/a":(200,"ok"),
        "/b":(201,"ok"),
    }
    y="""
    - proc:
        - GET: /<<p>>
          params:
            p: a     

    - call: proc # call a
      tests:
        status: 200

    - call: proc # call a  (pato will not be happy ;-) )
      params:
        p: b
      tests:
        status: 200
    """

    ll=Reqs(y,trace=True).execute(MOCK)
    # "b" is NOT priority over "a"
    for i in ll:
      assert all(i.tests)    

def test_create_default_value_for_proc(Reqs): # hey pato, look here
    MOCK={
        "/a":(200,"ok"),
        "/b":(201,"ok"),
    }
    y="""
    - proc:
        - GET: /<<p|defa>>
          params:
            defa: return "a" if x=="p" else x

    - call: proc # call a
      tests:
        status: 200

    - call: proc # call b  (pato will be happy ;-) )
      params:
        p: b
      tests:
        status: 201
    """

    ll=Reqs(y).execute(MOCK)
    # "b" is priority over "a"
    for i in ll:
      assert all(i.tests)    


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
    ll=Reqs(y,{"var":"first"},trace=True).execute(MOCK)
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
    

def test_priority_token(Reqs): # current major reqman's tests !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # PROBABLY THE MOST IMPORTANT TEST ;-)
    # (BASE FEATURE FROM DAY ONE)
    rc="""
    token: fake

    BEGIN:
      - GET: /token 
        save: token

    """

    y="""
    - call: BEGIN
    - GET: /<<token>>
      tests:
        status: 200
    - GET: /<<token>>
      params:
        token: real2  #override temporaly
      tests:
        status: 201
    - GET: /<<token>>
      tests:
        status: 200
    """
    MOCK={
        "/token":(200,'real'),
        "/real":(200,'ok'),
        "/real2":(201,'ok'),
    }
    ll=Reqs(y,Env(rc)).execute(MOCK)
    for i in ll:
      assert all(i.tests)
    