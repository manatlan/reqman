import reqman, asyncio, pytest
from pprint import pprint
import json

# 07/12/2020
# la recopi de dict ne marche pas comme je voudra
# je l'ai decouvert la, et voici un TU qui devrait
# normalement passe ...
# mais c pas le cas a l'heure actuelle


MOCK = {"/a/42": (200, "ok")}


def test_recopi_dico(exe):

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
#--------------------------
# test a simple value
#--------------------------
id: 42

id1: <<id>>

#--------------------------
# test a dict value
#--------------------------
user:
    id: 42
    name : kiki

user1: <<user>>

"""
        )

    with open("f.yml", "w+") as fid:
        fid.write(
            """
- GET: /a/<<id>>
  doc:  value=<<id>>
  tests:
    - status: 200

- GET: /a/<<id1>>
  doc:  value=<<id1>>
  tests:
    - status: 200

- GET: /a/<<user.id>>
  doc:  value=<<user.id>>
  tests:
    - status: 200

- GET: /a/<<user1.id>>
  doc:  value=<<user1.id>>
  tests:
    - status: 200

"""
        )

    x = exe(".", "--o", fakeServer=MOCK)
    # print(x.console)
    # x.view()
    assert x.rc == 0
