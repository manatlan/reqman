from context import reqs

SERVER={"/rien": (200,"hello")}

def test_1(reqs):
    l=reqs("""
- GET: http://supersite.fr/rien
  save: newVar
"""
    )

    env={}
    l[0].test(env)
    assert env == {'newVar': 'hello'}