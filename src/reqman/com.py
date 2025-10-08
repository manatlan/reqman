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

import httpx
import asyncio
import json
import logging
import ssl
import typing as T

logger = logging.getLogger(__name__)

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)

# a global cookie jar, to persist cookies between calls
_COOKIES = httpx.Cookies()

def init():
    _COOKIES.clear()
    # compatibility with old system, which required an init in an async loop
    class fake:
        async def __aenter__(self,*a,**k):
            pass
        async def __aexit__(self,*a,**k):
            pass
    return fake()

class Headers(httpx._models.Headers):
    def __getattr__(self, key):
        fix=lambda x: x and x.lower().strip().replace("-","_") or None
        for k,v in super().items():
            if fix(k)==fix(key):
                return v
        return super().__getitem__(key) 

class Response:
    def __init__(self, status:T.Optional[int], headers: Headers, content: bytes, info: str):
        assert isinstance(content, bytes)
        self.status=status
        self.headers=headers
        self.content=content
        self.info=info
        self.error=""

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.status}>"

class ResponseError(Response):
    def __init__(self,error):
        Response.__init__(self,None,Headers(),error.encode(),"")
        self.error=error
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


async def call(method, url:str, body: bytes=b'', headers:Headers=Headers(), timeout=None,proxies=None) -> Response:
    assert isinstance(body, bytes)

    try:
        async with httpx.AsyncClient(
            cookies=_COOKIES,
            verify=False,
            follow_redirects=False,
            proxy=proxies,
        ) as client:

            r = await client.request(
                method,
                url,
                content=body,
                headers=headers,
                timeout=timeout,
            )
            content = r.content
            try:
                # Try to decode json if the content type is correct
                if 'application/json' in r.headers.get('content-type', ''):
                    obj = r.json()
                    content = jdumps(obj).encode("utf-8")  # ensure json chars are not escaped, and are in utf8
            except (json.JSONDecodeError, TypeError):
                pass

            info = f"{r.http_version} {r.status_code} {r.reason_phrase}"

            return Response(r.status_code, Headers(r.headers), content, info)

    except httpx.ConnectError as e:
        logger.warning(f"Connection error for {url}: {e}")
        return ResponseUnreachable()
    except httpx.TimeoutException as e:
        logger.warning(f"Request to {url} timed out.")
        return ResponseTimeout()
    except (httpx.InvalidURL, httpx.UnsupportedProtocol) as e:
        logger.warning(f"Invalid URL '{url}': {e}")
        return ResponseInvalid(url)
    except ssl.SSLError:
        logger.warning(f"SSL Error for {url}")
        return ResponseUnreachable()
    except Exception as e:
        logger.error("Unhandled exception in call: %s (%s)",e, type(e))
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

            if isinstance(rep, (list, tuple)):
                if len(rep) == 2:
                    status, content = rep
                elif len(rep) == 3:
                    status, content, oHeaders = rep
                    outHeaders.update(oHeaders)
                else:
                    raise Exception("Bad mock response")
            else:
                raise Exception("Bad mock response")
        except Exception as e:
            status, content = 500, f"mock server error: {e}"
    assert isinstance(content, (str, bytes))
    assert isinstance(status, int)
    assert isinstance(outHeaders, dict)

    # ensure content is bytes
    if isinstance(content, str):
        #convert to bytes
        try:
            content=content.encode("cp1252").decode().encode()
        except:
            try:
                content=bytes(content,"utf8")
            except:
                raise Exception("Mock decoding str trouble")

    assert isinstance(content, bytes)

    info=f"MOCK/1.0 {status} RESPONSE"


    logger.debug(f"Simulate {method} {url} --> {status}")
    return Response(status,Headers(outHeaders),content,info)
    #####################################################################"


if __name__=="__main__":
    ...
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    # r=call_simulation( {"/":(200,"ok")},"GET","/" )
    # print("simul:",r)

    # async def t():
    #     e=await call("GET","https://httpstat.us/200?sleep=2000",timeout=1)
    #     print(e)
    #     e=await call("GET","https://www.manatlan.com")
    #     print(e)
    #     e=await call("GET","https://www.manatlan.com",proxies="http://77.232.100.132") # with a bad proxy ;-(
    #     print(e)

    # asyncio.run(t())

