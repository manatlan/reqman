#!/usr/bin/python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2025 manatlan manatlan[at]gmail(dot)com
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

class NotFound: pass

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)


def decodeBytes(b:bytes) -> str:
    assert isinstance(b, bytes)
    try:
        x=b.decode("utf8")
    except:
        try:
            x= b.decode("cp1252")
        except:
            x= str(b)
    assert isinstance(x, str)
    return x


if __name__=="__main__":
    ...
