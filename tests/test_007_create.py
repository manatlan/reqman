import pytest, reqman, json
import datetime,pickle

def test_simple():
  u="https://www.example.com/path?a=1&a=2&b=2#yo"
  conf,rml=reqman.create(u)
  assert "root:" in conf
  assert "User-Agent: reqman" in conf

  assert u in rml

def test_simple2():
  u="/path?a=1&a=2&b=2"
  conf,rml=reqman.create(u)
  assert conf is None

  assert u in rml

