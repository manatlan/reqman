#!/usr/bin/python3
# -*- coding: utf-8 -*-
import httpx
import json


AHTTP = httpx.AsyncClient(verify=False)

class Response:
    def __init__(self, status:int, headers: httpx.Headers, content: bytes, info: str):
        assert type(content)==bytes
        self.status=status
        self.headers=headers
        self.content=content
        self.info=info
        self.error=""

    def get_json(self):# -> any
        try:
            return json.loads(self.content.decode())
        except:
            return None

    def get_xml(self):
        #     try:
        #         return Xml(self.content.decode())
        #     except:
        #         return None
        return None


    def __repr__(self):
        return f"<{self.__class__.__name__} {self.status}>"

class ResponseError(Response):
    def __init__(self,error):
        Response.__init__(self,0,httpx.Headers(),b"","")
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
    def __init__(self):
        ResponseError.__init__(self,"Invalid")


async def call(method, url:str,body: bytes=b"", headers:dict={}, timeout=None) -> Response:
    assert type(body)==bytes

    try:
        r = await AHTTP.request(
            method,
            url,
            data=body,
            headers=headers,
            allow_redirects=False,
            timeout=timeout,
        )
        info = "%s %s %s" % (r.http_version, int(r.status_code), r.reason_phrase)
        return Response(r.status_code, r.headers, r.content, info)
    except (httpx.TimeoutException):
        return ResponseTimeout()
    except (httpx.ConnectError):
        return ResponseUnreachable()
    except (httpx.InvalidURL,httpx.UnsupportedProtocol,ValueError):
        return ResponseInvalid()


if __name__=="__main__":
    import asyncio
    async def t():
        e=await call("GET","https://www.manatlan.com")
        print(e)

    asyncio.run(t())