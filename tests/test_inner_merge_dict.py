#!/usr/bin/python
# -*- coding: utf-8 -*-
from context import reqman

def test_1():
    d1={
        "anum": 1,
        "headers": {
            "v1": 1
        },
        "headers1": {
            "v": 0
        },
        "mad": {
            "kif": [
                "kif1",
                "kif11"
            ],
            "use": {
                "v1": 1
            }
        },
        "test1": [
            {
                "status": 201
            }
        ],
        "tests": [
            {
                "status": 201
            }
        ]
    }

    d2={
        "anum": 2,
        "headers": {
            "v2": 2
        },
        "headers2": {
            "v": 0
        },
        "mad": {
            "kif": [
                "kif2",
                "kif22",
                "kif222"
            ],
            "use": {
                "v2": 2
            }
        },
        "test2": [
            {
                "status": 202
            }
        ],
        "tests": [
            {
                "status": 202
            }
        ]
    }


    d={}
    reqman.dict_merge(d,d1)
    reqman.dict_merge(d,d2)

    dd={ # print json.dumps( d2, indent=4, sort_keys=True )
        "anum": 2,
        "headers": {
            "v1": 1,
            "v2": 2
        },
        "headers1": {
            "v": 0
        },
        "headers2": {
            "v": 0
        },
        "mad": {
            "kif": [
                "kif1",
                "kif11",
                "kif2",
                "kif22",
                "kif222"
            ],
            "use": {
                "v1": 1,
                "v2": 2
            }
        },
        "test1": [
            {
                "status": 201
            }
        ],
        "test2": [
            {
                "status": 202
            }
        ],
        "tests": [
            {
                "status": 201
            },
            {
                "status": 202
            }
        ]
    }

    assert d == dd

