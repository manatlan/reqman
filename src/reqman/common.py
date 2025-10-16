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
        return b.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return b.decode("cp1252")
        except UnicodeDecodeError:
            # Fallback to latin-1, which can decode any byte
            return b.decode("latin-1")


if __name__=="__main__":
    ...
