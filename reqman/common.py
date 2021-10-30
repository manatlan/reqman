#!/usr/bin/python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2021 manatlan manatlan[at]gmail(dot)com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# https://github.com/manatlan/reqman
# #############################################################################

import json
import io

class NotFound: pass

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)


def decodeBytes(b:bytes) -> str:
    assert type(b)==bytes
    try:
        x=b.decode("utf8")
    except:
        try:
            x= b.decode("cp1252")
        except:
            x= str(b)
    assert type(x)==str
    return x

class FString(str):
    filename = None
    encoding = None

    def __new__(cls, fn: str):
        for e in ["utf8", "cp1252"]:
            try:
                with io.open(fn, "r", encoding=e) as fid:
                    obj = str.__new__(cls, fid.read())
                    obj.filename = fn
                    obj.encoding = e
                    return obj
            except UnicodeDecodeError:
                pass
        raise Exception("Can't read '%s'" % fn)

if __name__=="__main__":
    pass
