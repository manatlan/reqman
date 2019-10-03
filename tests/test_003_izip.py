import pytest, reqman, json

class Ex:
    def __init__(self,id):
        self.id=id
    def __repr__(self):
        return str(self.id)
    def __eq__(self,o):
        return (o and self.id==o.id)

    
def test_1():
    assert Ex(id=1) == Ex(id=1)
    assert Ex(id=1) != Ex(id=2)
    assert Ex(id=1) != None


def test_zip1():
    ex1 = [
        Ex(id=1),
    ]

    ex2 = [
    ]    

    assert "[(1, None)]" == str(reqman.izip(ex1,ex2))    
    assert not reqman.comparable(reqman.izip(ex1,ex2))

def test_zip2():
    ex1 = [
    ]

    ex2 = [
        Ex(id=1),
    ]    

    assert "[(None, 1)]" == str(reqman.izip(ex1,ex2))    
    assert not reqman.comparable(reqman.izip(ex1,ex2))

def test_zip():
    ex1 = [
        Ex(id=1),
        Ex(id=2),
        Ex(id=3),
    ]

    ex2 = [
        Ex(id=1),
        Ex(id=3),
        Ex(id=4),
        Ex(id=5),
    ]    

    assert "[(1, 1), (2, None), (3, 3), (None, 4), (None, 5)]" == str(reqman.izip(ex1,ex2))
    assert reqman.comparable(reqman.izip(ex1,ex2))

    ex1 = [
        Ex(id=1),
        Ex(id=3),
        Ex(id=4),
        Ex(id=5),
    ]    

    ex2 = [
        Ex(id=1),
        Ex(id=2),
        Ex(id=3),
    ]

    assert "[(1, 1), (None, 2), (3, 3), (4, None), (5, None)]" == str(reqman.izip(ex1,ex2))
    assert reqman.comparable(reqman.izip(ex1,ex2))


def test_zip_same():
    ex1 = [
        Ex(id=1),
        Ex(id=1),
        Ex(id=1),
    ]

    ex2 = [
        Ex(id=1),
        Ex(id=1),
        Ex(id=1),
    ]    

    assert "[(1, 1), (1, 1), (1, 1)]" == str(reqman.izip(ex1,ex2))
    assert reqman.comparable(reqman.izip(ex1,ex2))

def test_zip_nimp():
    ex1 = [
        Ex(id=1),
    ]

    ex2 = [
        Ex(id=2),
    ]    

    assert "[(1, None), (None, 2)]" == str(reqman.izip(ex1,ex2))
    assert not reqman.comparable(reqman.izip(ex1,ex2))
