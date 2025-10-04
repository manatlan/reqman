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

import httpx
import asyncio
import json
import logging

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    return json.dumps(o, *a, **k)

COOKIE_JAR = None

def init():
    global COOKIE_JAR
    if COOKIE_JAR is None:
        COOKIE_JAR = httpx.Cookies()

    class fake:
        async def __aenter__(self,*a,**k):
            pass
        async def __aexit__(self,*a,**k):
            pass
    return fake()

def reset():
    global COOKIE_JAR
    COOKIE_JAR = None

class Response:
    def __init__(self, status:int, headers: dict, content: bytes, info: str):
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
        super().__init__(None,{},str(error).encode(),"")
        self.error = str(error)
    def get_json(self):
        return None
    def get_xml(self):
        return None
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.error}>"

class ResponseTimeout(ResponseError):
    def __init__(self):
        super().__init__("Timeout")

class ResponseUnreachable(ResponseError):
    def __init__(self):
        super().__init__("Unreachable")

class ResponseInvalid(ResponseError):
    def __init__(self,url):
        super().__init__(f"Invalid {url}")

async def call(method, url:str, body: bytes=b'', headers:dict={}, timeout=None,proxies=None) -> Response:
    assert isinstance(body, bytes)
    if COOKIE_JAR is None: init()

    try:
        client_args = {
            "trust_env": True,
            "follow_redirects": False,
            "verify": False,
            "cookies": COOKIE_JAR,
        }

        if proxies:
            if "socks" in proxies:
                try:
                    from httpx_socks import AsyncProxyTransport
                    client_args["transport"] = AsyncProxyTransport.from_url(proxies)
                except ImportError:
                    return ResponseError("httpx-socks is not installed. Please install it with 'pip install httpx-socks'")
            else:
                client_args["proxies"] = {'http://': proxies, 'https://': proxies}

        async with httpx.AsyncClient(**client_args) as session:

            r = await session.request(
                method,
                url,
                content=body,
                headers=headers,
                timeout=timeout,
            )
            COOKIE_JAR.update(r.cookies)

            try:
                obj = r.json()
                content = jdumps(obj).encode("utf-8")
            except (json.JSONDecodeError, UnicodeDecodeError):
                content = r.content

            http_version = r.http_version.split('/')[1] if r.http_version and r.http_version.startswith("HTTP/") else "1.1"
            info = f"HTTP/{http_version} {r.status_code} {r.reason_phrase}"

            return Response(r.status_code, r.headers, content, info)

    except httpx.ConnectError:
        return ResponseUnreachable()
    except httpx.TimeoutException:
        return ResponseTimeout()
    except (httpx.InvalidURL, httpx.UnsupportedProtocol):
        return ResponseInvalid(url)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return ResponseUnreachable()

def call_simulation(http, method, url:str,body: bytes=b"", headers:dict={}):
    status, content, outHeaders = (404, "mock not found", {"server": "reqman mock"})

    if url in http:
        rep = http[url]
        try:
            if callable(rep):
                rep = rep(method, url, body, headers)

            if len(rep) == 2:
                status, content = rep
            elif len(rep) == 3:
                status, content, oHeaders = rep
                outHeaders.update(oHeaders)
            else:
                raise Exception("Bad mock response")
        except Exception as e:
            status, content = 500, f"mock server error: {e}"

    if isinstance(content, str):
        try:
            content=content.encode("cp1252").decode().encode()
        except:
            try:
                content=bytes(content,"utf8")
            except:
                raise Exception("Mock decoding str trouble")

    assert isinstance(content, bytes)
    info=f"MOCK/1.0 {status} RESPONSE"
    logging.debug(f"Simulate {method} {url} --> {status}")
    return Response(status, outHeaders, content, info)

if __name__=="__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    r=call_simulation( {"/":(200,"ok")},"GET","/" )
    print("simul:",r)

    async def t():
        init()
        e=await call("GET","https://httpstat.us/200?sleep=2000",timeout=1)
        print(e)
        e=await call("GET","https://www.manatlan.com")
        print(e)
        e=await call("GET","https://www.manatlan.com",proxies="http://77.232.100.132")
        print(e)

    asyncio.run(t())