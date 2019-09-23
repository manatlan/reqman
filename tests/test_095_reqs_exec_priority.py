from reqman import Reqs

MOCK={
    "https://yo/a":(200,"ok"),
    "https://yo/b":(201,"ok"),
}

def test_priority(Reqs):
    y="""
    - proc:
        - GET: https://yo/<<p>>
          params:
            p: a
    - call: proc
      params:
        p: b
      tests:
        status: 201
    """

    ll=Reqs(y,trace=True).execute(MOCK)
    assert all(ll[0].tests) # "b" is priority over "a"
