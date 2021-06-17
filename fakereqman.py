##/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp import web
import json,asyncio
import os, tempfile, shutil

routes = web.RouteTableDef()

@routes.post('/ping')
async def hello(request):
    b=await request.read()
    return web.Response(status=201,body=b,headers=request.headers)


@routes.get('/set')
async def hello(request):
    return web.Response(status=200,text=request.query.get("value","?"))

@routes.get('/cookie')
async def cookie(request):
    resp=web.Response(status=200,text="?")

    argv=request.query.get("value","?")
    if argv=="create":
        resp.set_cookie("cpt",0)
        msg= "create"
    elif argv=="inc":
        cpt=int(request.cookies.get("cpt",-1))
        if cpt>=0:
            resp.set_cookie("cpt",cpt+1)
            msg="inc"
        else:
            msg="no"
    elif argv=="view":
        cpt=int(request.cookies.get("cpt",-1))
        if cpt>=0:
            msg=str(cpt)
        else:
            msg="no"
    elif argv=="del":
        resp.del_cookie("cpt")
        msg="del"
    else:
        msg="???"

    resp.text=msg
    return resp

@routes.get('/bigtxt')
async def hello(request):
    return web.Response(status=200,text="".join(["[%s]" % i for i in range(10000)]))

@routes.get('/wait')
async def hello(request):
    await asyncio.sleep(float(request.query.get("value","5")))
    return web.Response(status=200,text="OK" )

@routes.get('/get_404')
async def hello(request):
    return web.Response(status=404,text="My not found")

@routes.get('/get_500')
async def hello(request):
    a=12/0


@routes.get('/get_txt')
async def hello(request):
    return web.Response(status=200,text="Héllo ça và ?")

@routes.get('/get_txt_cp1252')
async def hello(request):
    return web.Response(status=200,text="Héllo ça và ?",charset="Windows-1252")

@routes.get('/get_bytes')
async def hello(request):
    return web.Response(status=200,body=bytes(range(0,255)) )

@routes.get('/get_json')
async def hello(request):
    obj=dict( info=dict(t="Hello",n=42,m="42"), infos=[1,2,3], float=3.14, empty=None, mot="héllo ça va ?",msg="héllo")
    return web.Response(status=200,body=json.dumps(obj),headers={"X-MyHeader":"hello"})

@routes.get('/get_header')
async def hello(request):
    return web.Response(status=200,body="ok", headers=dict(msg="héhé"))

@routes.get('/get_xml')
async def hello(request):
    xml="""<?xml version="1.0" encoding="UTF-8"?>
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
    return web.Response(status=200,text=xml)

import socket
def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    return not (s.connect_ex((ip,port)) == 0)

import sys,reqman
import threading,asyncio
class FakeWebServer(threading.Thread): # the webserver is ran on a separated thread
    def __init__(self,port):
        super(FakeWebServer, self).__init__()
        self.port=port
        self.app = web.Application()
        self.app.add_routes(routes)
        self.root="http://localhost:%s" % self.port
        self._exit=False

    def run(self):
        print("> Fake Server:",self.root)

        async def start():
            runner = web.AppRunner(self.app)
            await runner.setup()
            self.site=web.TCPSite(runner, 'localhost', self.port)
            await self.site.start()

            while self._exit==False:
                await asyncio.sleep(0.333333)

            await self.site.stop()
            await runner.shutdown()

        asyncio.set_event_loop(asyncio.new_event_loop())
        loop=asyncio.get_event_loop()


        async def wait():
            while not isFree("127.0.0.1",self.port):
                await asyncio.sleep(0.5)

        loop.run_until_complete(wait())
        loop.run_until_complete(start())
        loop.run_until_complete(wait())

        # gracefull death
        tasks = asyncio.all_tasks(loop) #py37
        for task in tasks: task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*tasks))
        except:
            pass
        loop.close()


    def stop(self):
        self._exit=True





def checkSign(sign1,sign2,args):
    """ Return the error or '' """
    if sign1==sign2:
        return "" # no error
    else:
        dsign1=sign1.split(',')
        dsign2=sign2.split(',')
        if len(dsign1)!=len(dsign2):
            return "Not same number of requests (is there a new ?), for %s" % args
        else:
            for idx,(t1,t2) in enumerate(zip(dsign1,dsign2)):
                if len(t1) != len(t2):
                    return "Req %s has %s tests (expected %s), for %s" % (idx+1,len(t2),len(t1),args)
                else:
                    if t1!=t2:
                        diffs=[i+1 for i,(a1,a2)  in enumerate(zip(t1,t2)) if a1!=a2]
                        return "Req %s fail on its %s test, for %s" % (idx+1,diffs[0],args)

def main( file, avoidBrowser=True ):
    """
    yield "" : si valid est ok
    yield "error" : si valid est ko
    yield None : si pas validation
    """

    class RR:
        rr=None
    o=RR()

    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ NEW SYSTEM
    newValids=[i[8:i.rfind('#') or None].strip().split() for i in reqman.FString(file).splitlines() if i.startswith("#:valid:")]
    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ NEW SYSTEM
    try:
        precdir = os.getcwd()
        testdir = tempfile.mkdtemp()
        os.chdir( testdir )



        for newValid in newValids:
            valid,*args=newValid
            args=[file if i=="THIS" else i for i in args]
            if avoidBrowser==True and "--b" in args: args.remove("--b") # remove --b when pytest ;-)
            sys.argv = ["reqman"] + args

            rc=reqman.main(hookResults=o)
            if rc>=0:
                if hasattr(o,"rr"):
                    details=[]
                    details2=[]
                    if o.rr and o.rr.results:
                        for i in o.rr.results:
                            for j in i.exchanges:
                                if type(j)==tuple:
                                    if j[0]: details.append("".join([str(int(t)) for t in j[0].tests]))
                                    if j[1]: details2.append("".join([str(int(t)) for t in j[1].tests]))
                                else:
                                    details.append("".join([str(int(t)) for t in j.tests]))
                        toValid=",".join(details)
                        if details2: toValid+=":"+",".join(details2)

                        if valid:
                            err=checkSign(valid,toValid,args)
                            print("> Check valid:",valid,"?==",toValid,"-->","!!! ERROR: %s !!!"%err if err else "OK")
                        else:
                            print("> No validation check! (valid:%s)" % toValid)
                            err=None
                    else:
                        err=None
                else:
                    err=""    #TODO: do something here (see test "new url")
            else:
                toValid="ERROR"
                if valid:
                    err="" if valid==toValid else "mismatch (%s!=%s, for %s)" % (valid,toValid,args)
                    print("> Check valid:",valid,"?==",toValid,"-->","!!! ERROR: %s !!!"%err if err else "OK")
                else:
                    print("> No validation check! (valid:%s)" % toValid)
                    err=None

            yield err

    finally:
        os.chdir( precdir )
        shutil.rmtree(testdir)


if __name__=="__main__":

    # sys.argv=["","REALTESTS/auto_new_response_request.yml"] # *** FOR running in DEDUG MODE ***

    try:
        ws=FakeWebServer(11111)
        ws.start()
        import time
        time.sleep(1) # wait server start ;-(

        for err in main(sys.argv[1],avoidBrowser=False):
            if err is None:
                sys.exit( -1)
            elif err:
                sys.exit(1)
        print("*** ALL IS OK ***")
        sys.exit(0)
    finally:
        ws.stop()

