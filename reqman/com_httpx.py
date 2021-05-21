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


####################################################################### this file is never used, yet !
# HERE, it's the future, thru HTTPX
# but since httpx doens't support socks proxy
# I give up, and come back to aiohttp ;-(
#######################################################################
import httpx
import json
import logging



def init(): # here, it's horrible !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    AHTTP = httpx.AsyncClient(verify=False)
    return AHTTP

AHTTP = init()

class Response:
    def __init__(self, status:int, headers: httpx.Headers, content: bytes, info: str):
        assert type(content)==bytes
        self.status=status
        self.headers=headers
        self.content=content
        self.info=info
        self.error=""

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.status}>"

class ResponseError(Response):
    def __init__(self,error):
        Response.__init__(self,None,httpx.Headers(),error.encode(),"")
    def get_json(self):
        return None
    def get_xml(self):
        return None
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.error}>"

class ResponseTimeout(ResponseError):
    def __init__(self):
        ResponseError.__init__(self,"Timeout")

class ResponseUnreachable(ResponseError):
    def __init__(self):
        ResponseError.__init__(self,"Unreachable")

class ResponseInvalid(ResponseError):
    def __init__(self,url):
        ResponseError.__init__(self,f"Invalid {url}")


#TODO: wtf ?
textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
isBytes = lambda bytes: bool(bytes.translate(None, textchars))

async def call(method, url:str,body: bytes=b"", headers:dict={}, timeout=None, proxies=None) -> Response:
    assert type(body)==bytes
    try:

        AHTTP._get_proxy_map(proxies, False)

        r = await AHTTP.request(
            method,
            url,
            data=body,
            headers=headers,
            allow_redirects=False,
            timeout=timeout,   # sec to millisec
        )

        info = "%s %s %s" % (r.http_version, int(r.status_code), r.reason_phrase)

        content=r.content
        if not isBytes(content):
            txt = r.text
            content = txt.encode("utf-8")  # force bytes to be in utf8

        return Response(r.status_code, r.headers, content, info)
    except (httpx.TimeoutException):
        return ResponseTimeout()
    except (httpx.ConnectError):
        return ResponseUnreachable()
    except (httpx.InvalidURL,httpx.UnsupportedProtocol,ValueError):
        return ResponseInvalid(url)


def call_simulation(http, method, url:str,body: bytes=b"", headers:dict={}):
    #simulate with http hook
    #####################################################################"
    status, content, outHeaders = ( # default response 404
        404,
        "mock not found",
        {"server": "reqman mock"},
    )

    if url in http:
        rep = http[url]
        try:
            if callable(rep):
                rep = rep(method, url, body, headers)

            if len(rep) == 2:
                status, content = rep
            elif len(rep) == 3:
                status, content, oHeaders = rep
                outHeaders.update( oHeaders )
            else:
                raise Exception("Bad mock response")
        except Exception as e:
            status, content = 500, f"mock server error: {e}"
    assert type(content) in [str, bytes]
    assert type(status) is int
    assert type(outHeaders) is dict

    # ensure content is bytes
    if type(content)==str:
        #convert to bytes
        try:
            content=content.encode("cp1252").decode().encode()
        except:
            try:
                content=bytes(content,"utf8")
            except:
                raise Exception("Mock decoding str trouble")

    assert type(content)==bytes

    info=f"MOCK/1.0 {status} RESPONSE"


    logging.debug(f"Simulate {method} {url} --> {status}")
    return Response(status,outHeaders,content,info)
    #####################################################################"


if __name__=="__main__":
    import asyncio

    import logging
    logging.basicConfig(level=logging.DEBUG)

    async def t():
        e=await call("GET","https://www.manatlan.com")
        print(e)
        e=await call("GET","https://www.manatlan.com",proxies="http://77.232.100.132") # with a valid proxy
        print(e)

    asyncio.run(t())

    r=call_simulation( {"/":(200,"ok")},"GET","/" )
    print(r)