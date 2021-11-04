import pytest,reqman


def test_simplest(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com
      params:
        p1: 1
- call: proc
  params:
        p2: 2

"""
    l=Reqs(y)
    if l._old:
      assert len(l) == 1
      assert l[0].reqs[0].params ==  {'p1': 1}
    else:
      assert len(l) == 2
      #TODO: do better here

def test_simplest2(Reqs):
    y="""
- proc:
    - GET: https://www.manatlan.com/<<p1>>/<<p>>/<<p2>>
      params:
        p1: p1
- call: proc
  foreach:
    - p: 1
    - p: 2
  params:
    p2: p2

"""
    l=Reqs(y)
    if l._old:
      assert len(l) == 1
      assert l[0].foreach == [{'p': 1}, {'p': 2}] # foreach params
      assert l[0].reqs[0].params == {'p1': 'p1'}

      MOCK={"https://www.manatlan.com/p1/1/p2":(200,"ok"),"https://www.manatlan.com/p1/2/p2":(200,"ok")}
      ll=l.execute( MOCK )
      assert ll[0].status==200
      assert ll[1].status==200
      assert ll[0].url == "https://www.manatlan.com/p1/1/p2"
      assert ll[1].url == "https://www.manatlan.com/p1/2/p2"
    else:
      pass
      #TODO: do better here
