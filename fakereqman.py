##/usr/bin/python
# -*- coding: utf-8 -*-

from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
import json
import asyncio
import os
import tempfile
import shutil
import uvicorn
import time

async def ping(request):
    """
    This endpoint is used to test the connection.
    It returns a 201 status code with the request body and headers.
    To use it, send a POST request to /ping with any body.
    """
    b = await request.body()
    return Response(status_code=201, content=b, headers=dict(request.headers))

async def set_value(request):
    """
    This endpoint returns the value of the 'value' query parameter.
    To use it, send a GET request to /set?value=your_value.
    If the 'value' parameter is not provided, it returns '?'.
    """
    return Response(status_code=200, content=request.query_params.get("value", "?"))

async def cookie(request):
    """
    This endpoint is used to manage cookies.
    It can create, increment, view, and delete a cookie named 'cpt'.
    To use it, send a GET request to /cookie?value=[create|inc|view|del].
    - 'create': creates the 'cpt' cookie with a value of '0'.
    - 'inc': increments the value of the 'cpt' cookie.
    - 'view': returns the value of the 'cpt' cookie.
    - 'del': deletes the 'cpt' cookie.
    """
    argv = request.query_params.get("value", "?")

    if argv == "create":
        resp = Response(status_code=200, content="create")
        resp.set_cookie("cpt", "0", path="/")
        return resp

    if argv == "inc":
        cpt = int(request.cookies.get("cpt", -1))
        if cpt >= 0:
            resp = Response(status_code=200, content="inc")
            resp.set_cookie("cpt", str(cpt + 1), path="/")
            return resp
        else:
            return Response(status_code=200, content="no")

    if argv == "view":
        cpt = request.cookies.get("cpt", "no")
        return Response(status_code=200, content=str(cpt))

    if argv == "del":
        resp = Response(status_code=200, content="del")
        resp.delete_cookie("cpt", path="/")
        return resp

    return Response(status_code=200, content="???")

async def bigtxt(request):
    """
    This endpoint returns a large text response.
    To use it, send a GET request to /bigtxt.
    """
    return Response(status_code=200, content="".join(["[%s]" % i for i in range(10000)]))

async def wait(request):
    """
    This endpoint waits for a specified amount of time before returning a response.
    To use it, send a GET request to /wait?value=seconds.
    If the 'value' parameter is not provided, it waits for 5 seconds.
    """
    await asyncio.sleep(float(request.query_params.get("value", "5")))
    return Response(status_code=200, content="OK")

async def get_404(request):
    """
    This endpoint always returns a 404 Not Found response.
    To use it, send a GET request to /get_404.
    """
    return Response(status_code=404, content="My not found")

async def get_500(request):
    """
    This endpoint always returns a 500 Internal Server Error response.
    To use it, send a GET request to /get_500.
    """
    a = 12 / 0

async def get_txt(request):
    """
    This endpoint returns a simple text response with UTF-8 encoding.
    To use it, send a GET request to /get_txt.
    """
    return Response(status_code=200, content="Héllo ça và ?")

async def get_txt_cp1252(request):
    """
    This endpoint returns a text response with Windows-1252 encoding.
    To use it, send a GET request to /get_txt_cp1252.
    """
    return Response(status_code=200, content="Héllo ça và ?", media_type="text/plain; charset=Windows-1252")

async def get_bytes(request):
    """
    This endpoint returns a byte stream.
    To use it, send a GET request to /get_bytes.
    """
    return Response(status_code=200, content=bytes(range(0, 255)), media_type="application/octet-stream")

async def get_json(request):
    """
    This endpoint returns a JSON response.
    To use it, send a GET request to /get_json.
    """
    obj = dict(info=dict(t="Hello", n=42, m="42"), infos=[1, 2, 3], float=3.14, empty=None, mot="héllo ça va ?", msg="héllo")
    return JSONResponse(status_code=200, content=obj, headers={"X-MyHeader": "hello"})

async def get_header(request):
    """
    This endpoint returns a response with a custom header.
    To use it, send a GET request to /get_header.
    The response will contain the header 'msg: héhé'.
    """
    return Response(status_code=200, content="ok", headers=dict(msg="héhé"))

async def get_xml(request):
    """
    This endpoint returns an XML response.
    To use it, send a GET request to /get_xml.
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<x xmlns:ns2="www">
    <entete>
        <ns2:typeDocument>hello</ns2:typeDocument>
    </entete>
    <age>42</age>
    <a v="1">aaa1</a>
    <a>aaa2</a>
    <b v="9">b9</b>
    <b v="11">b11</b>
    <c>yolo <i>xxx</i></c>
</x>"""
    return Response(status_code=200, content=xml)

BDD = {
    1: "toto1",
    2: "toto2",
    3: "toto3"
}

async def get_list(request):
    """
    This endpoint returns a list of items from the BDD dictionary.
    To use it, send a GET request to /get_list.
    """
    obj = dict(items=[dict(id=k, name=v) for k, v in BDD.items()])
    return JSONResponse(status_code=200, content=obj)

async def get_item(request):
    """
    This endpoint returns a specific item from the BDD dictionary.
    To use it, send a GET request to /item/{item_id}.
    If the item is not found, it returns a 404 error.
    """
    try:
        idx = int(request.path_params['item'])
        obj = dict(id=idx, name=BDD[idx])
        return JSONResponse(status_code=200, content=obj)
    except:
        return Response(status_code=404, content="no item found")

routes = [
    Route('/ping', endpoint=ping, methods=['POST']),
    Route('/set', endpoint=set_value, methods=['GET']),
    Route('/cookie', endpoint=cookie, methods=['GET']),
    Route('/bigtxt', endpoint=bigtxt, methods=['GET']),
    Route('/wait', endpoint=wait, methods=['GET']),
    Route('/get_404', endpoint=get_404, methods=['GET']),
    Route('/get_500', endpoint=get_500, methods=['GET']),
    Route('/get_txt', endpoint=get_txt, methods=['GET']),
    Route('/get_txt_cp1252', endpoint=get_txt_cp1252, methods=['GET']),
    Route('/get_bytes', endpoint=get_bytes, methods=['GET']),
    Route('/get_json', endpoint=get_json, methods=['GET']),
    Route('/get_header', endpoint=get_header, methods=['GET']),
    Route('/get_xml', endpoint=get_xml, methods=['GET']),
    Route('/get_list', endpoint=get_list, methods=['GET']),
    Route('/item/{item}', endpoint=get_item, methods=['GET']),
]

app = Starlette(routes=routes)

import socket

def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        return s.connect_ex((ip, port)) != 0
    finally:
        s.close()

import sys, reqman
import threading

class FakeWebServer(threading.Thread):
    def __init__(self, port):
        super(FakeWebServer, self).__init__()
        self.port = port
        self.root = "http://localhost:%s" % self.port
        self.config = uvicorn.Config(app, host="localhost", port=self.port, log_level="warning")
        self.server = uvicorn.Server(self.config)
        self._exit = False

    def run(self):
        print("> Fake Server:", self.root)
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def checkSign(sign1, sign2, args):
    """ Return the error or '' """
    if sign1 == sign2:
        return ""  # no error
    else:
        dsign1 = sign1.split(',')
        dsign2 = sign2.split(',')
        if len(dsign1) != len(dsign2):
            return "Not same number of requests (is there a new ?), for %s" % args
        else:
            for idx, (t1, t2) in enumerate(zip(dsign1, dsign2)):
                if len(t1) != len(t2):
                    return "Req %s has %s tests (expected %s), for %s" % (idx + 1, len(t2), len(t1), args)
                else:
                    if t1 != t2:
                        diffs = [i + 1 for i, (a1, a2) in enumerate(zip(t1, t2)) if a1 != a2]
                        return "Req %s fail on its %s test, for %s" % (idx + 1, diffs[0], args)

def main(file, avoidBrowser=True):
    """
    yield "" : si valid est ok
    yield "error" : si valid est ko
    yield None : si pas validation
    """

    class RR:
        rr = None
    o = RR()

    newValids = [i[8:i.rfind('#') or None].strip().split() for i in reqman.FString(file).splitlines() if i.startswith("#:valid:")]
    try:
        precdir = os.getcwd()
        testdir = tempfile.mkdtemp()
        os.chdir(testdir)

        for newValid in newValids:
            valid, *args = newValid
            args = [file if i == "THIS" else i for i in args]
            if avoidBrowser and "--b" in args:
                args.remove("--b")
            sys.argv = ["reqman"] + args

            rc = reqman.main(hookResults=o)
            if rc >= 0:
                if hasattr(o, "rr") and o.rr and o.rr.results:
                    details = []
                    details2 = []
                    for i in o.rr.results:
                        for j in i.exchanges:
                            if isinstance(j, tuple):
                                if j[0]:
                                    details.append("".join([str(int(t)) for t in j[0].tests]))
                                if j[1]:
                                    details2.append("".join([str(int(t)) for t in j[1].tests]))
                            else:
                                details.append("".join([str(int(t)) for t in j.tests]))
                    toValid = ",".join(details)
                    if details2:
                        toValid += ":" + ",".join(details2)

                    if valid:
                        err = checkSign(valid, toValid, args)
                        print("> Check valid:", valid, "?==", toValid, "-->", "!!! ERROR: %s !!!" % err if err else "OK")
                    else:
                        print("> No validation check! (valid:%s)" % toValid)
                        err = None
                else:
                    err = ""
            else:
                toValid = "ERROR"
                if valid:
                    err = "" if valid == toValid else "mismatch (%s!=%s, for %s)" % (valid, toValid, args)
                    print("> Check valid:", valid, "?==", toValid, "-->", "!!! ERROR: %s !!!" % err if err else "OK")
                else:
                    print("> No validation check! (valid:%s)" % toValid)
                    err = None
            yield err
    finally:
        os.chdir(precdir)
        time.sleep(0.1)
        shutil.rmtree(testdir)

if __name__ == "__main__":
    try:
        ws = FakeWebServer(11111)
        ws.start()
        import time
        time.sleep(1)

        for err in main(sys.argv[1], avoidBrowser=False):
            if err is None:
                sys.exit(-1)
            elif err:
                sys.exit(1)
        print("*** ALL IS OK ***")
        sys.exit(0)
    finally:
        ws.stop()