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

import aiohttp  # see "pip install aiohttp"
import asyncio
import json
import logging
import concurrent
import ssl

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)

JAR=None

def init():
    global JAR
    JAR = aiohttp.CookieJar(unsafe=True)
    class fake:
        async def __aenter__(self,*a,**k):
            pass
        async def __aexit__(self,*a,**k):
            pass
    return fake()

init()

class Response:
    def __init__(self, status:int, headers: dict, content: bytes, info: str):
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
        Response.__init__(self,None,{},error.encode(),"")
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


async def call(method, url:str, body: bytes=b'', headers:dict={}, timeout=None,proxies=None) -> Response:
    assert type(body)==bytes
    try:
        async with aiohttp.ClientSession(trust_env=True,cookie_jar=JAR) as session:

            r = await session.request(
                method,
                url,
                data=body,
                headers=headers,
                ssl=False,
                timeout=timeout,
                allow_redirects=False,
                proxy=proxies
            )
            try:
                obj = await r.json()
                content = jdumps(obj).encode("utf-8")  # ensure json chars are not escaped, and are in utf8
            except:
                content = await r.read()
                if not isBytes(content):
                    txt = await r.text()
                    content = txt.encode("utf-8")  # force bytes to be in utf8

            info = "HTTP/%s.%s %s %s" % (
                r.version.major,
                r.version.minor,
                int(r.status),
                r.reason,
            )
            outHeaders = r.headers

            return Response(r.status, r.headers, content, info)

    except aiohttp.client_exceptions.ClientConnectorError as e:
        return ResponseUnreachable()
    except (concurrent.futures._base.TimeoutError, asyncio.exceptions.TimeoutError) as e:
        return ResponseTimeout()
    except aiohttp.client_exceptions.InvalidURL as e:
        return ResponseInvalid(url)
    except ssl.SSLError:
        pass
    except:
        return ResponseUnreachable()



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

    import logging
    logging.basicConfig(level=logging.DEBUG)

    r=call_simulation( {"/":(200,"ok")},"GET","/" )
    print("simul:",r)

    async def t():
        e=await call("GET","https://httpstat.us/200?sleep=2000",timeout=1)
        print(e)
        e=await call("GET","https://www.manatlan.com")
        print(e)
        e=await call("GET","https://www.manatlan.com",proxies="http://77.232.100.132") # with a bad proxy ;-(
        print(e)

    asyncio.run(t())

