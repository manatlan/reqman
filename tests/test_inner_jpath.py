#!/usr/bin/python
# -*- coding: utf-8 -*-
import reqman
def test_1():
        d=reqman.yaml.load("""
        toto:
            val1: 100
            val2: 200
            val3: null

        titi:
            - v1
            - v2:
                a: 1
                b: 2

        whos:
            - pers1:
                name: jo
                age: 42
            - pers2:
                name: jack
                age: 43

        astring: hello
        anumber: 42
        abool: true
        anone: null

        """)
        assert reqman.jpath(d,"tata") == reqman.NotFound 
        assert reqman.jpath(d,"toto.val1") == 100 
        assert reqman.jpath(d,"toto.val2") == 200 
        assert reqman.jpath(d,"toto.val3") == None 
        assert reqman.jpath(d,"toto.val4") == reqman.NotFound 
        assert reqman.jpath(d,"toto.0") == reqman.NotFound 
        assert reqman.jpath(d,"toto.1") == reqman.NotFound 
        assert reqman.jpath(d,"toto.2") == reqman.NotFound 
        assert reqman.jpath(d,"toto") == {'val2': 200, 'val1': 100, 'val3':None} 

        assert reqman.jpath(d,"titi") == ['v1', {'v2': {'a': 1, 'b': 2}}] 
        assert reqman.jpath(d,"titi.0") == "v1" 
        assert reqman.jpath(d,"titi.1") == {'v2': {'a': 1, 'b': 2}} 
        assert reqman.jpath(d,"titi.1.v2") == {'a': 1, 'b': 2} 
        assert reqman.jpath(d,"titi.1.v2.b") ,2 
        assert reqman.jpath(d,"titi.2") == reqman.NotFound 

        assert reqman.jpath(d,"astring") == "hello" 
        assert reqman.jpath(d,"astring.var") == "hello" 
        assert reqman.jpath(d,"astring.0") == "hello" 
        assert reqman.jpath(d,"astring.var.cvx.vcx.fgsd") == "hello" 

        assert reqman.jpath(d,"anumber") == 42 
        assert reqman.jpath(d,"anumber.var") == 42 
        assert reqman.jpath(d,"anumber.0") == 42 
        assert reqman.jpath(d,"anumber.var.cvx.vcx.fgsd") == 42 

        assert reqman.jpath(d,"abool") == True 
        assert reqman.jpath(d,"abool.var") == True 
        assert reqman.jpath(d,"abool.0") == True 
        assert reqman.jpath(d,"abool.var.cvx.vcx.fgsd") == True 

        assert reqman.jpath(d,"anone") == None 
        assert reqman.jpath(d,"anone.var") == None 
        assert reqman.jpath(d,"anone.0") == None 
        assert reqman.jpath(d,"anone.var.cvx.vcx.fgsd") == None 

        assert reqman.jpath(d,"whos.0.pers1.name") == "jo" 

        # test ".size"
        assert reqman.jpath(d,"whos.size") == 2          # 2 items in that list
        assert reqman.jpath(d,"whos.0.size") == 1        # one key in that dict
        assert reqman.jpath(d,"whos.0.pers1.size") == 2  # 2 keys in this dicts
        assert reqman.jpath(d,"astring.size") == 5      # size of the string 
        assert reqman.jpath(d,"anumber.size") == 42     # unknown key for a number return content, see ^
        assert reqman.jpath(d,"abool.size") == True     # unknown key for a bool return content, see ^
        assert reqman.jpath(d,"anone.size") == None     # unknown key for a null return content, see ^
        assert reqman.jpath(d,"unknown.size") == reqman.NotFound     # unknown key for a unknown return NotFound, see ^
        assert reqman.jpath(d,".size") == 7     # .size at the root --> 7 keys
        assert reqman.jpath(d,"size") == 7     # size is assimilatted to .size, so -> 7

