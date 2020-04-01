##/usr/bin/python
# -*- coding: utf-8 -*-

    
from aiohttp import web
import json,asyncio

routes = web.RouteTableDef()

@routes.get('/set')
async def hello(request):
    return web.Response(status=200,text=request.query.get("value","?"))

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
    return web.Response(status=200,body=json.dumps(obj))

@routes.get('/get_header')
async def hello(request):
    return web.Response(status=200,body="ok", headers=dict(msg="héhé"))

@routes.get('/get_xml')
async def hello(request):
    xml="""<root>
        <name prefix="mr">john</name>
        <age>42</age>
        <infos rep="héllo" ref="1515">
            <info v="0"></info>
            <info v="1">3.14</info>
            <info v="2">Hello</info>
            <info v="3">Héllo</info>
        </infos>
    </root>
    """
    return web.Response(status=200,text=xml)


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
        print("Fake Server:",self.root)

        async def start():
            runner = web.AppRunner(self.app)
            await runner.setup()
            await web.TCPSite(runner, 'localhost', self.port).start()
        
            while self._exit==False:
                await asyncio.sleep(0.1)

        asyncio.set_event_loop(asyncio.new_event_loop())
        loop=asyncio.get_event_loop()
        loop.run_until_complete(start())        


        # gracefull death
        try:
            tasks = asyncio.all_tasks(loop) #py37
        except:
            tasks = asyncio.Task.all_tasks(loop) #py35
        for task in tasks: task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*tasks))
        except:
            pass


    def stop(self):
        self._exit=True

def main():
    """
    retourne 0 : si valid est ok
    retourne 1 : si valid est ko
    retourne None : si pas validation
    """

    ws=FakeWebServer(11111)

    class RR: pass
    o=RR()

    #check valid in argv -> valid
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    removeArgIdx=None
    valid=None
    for idx, argv in enumerate(sys.argv):
        if argv.startswith("valid:"):
            valid = argv[6:]
            removeArgIdx=idx
    if removeArgIdx:
        del sys.argv[removeArgIdx]
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    try:
        ws.start()
        rc=reqman.main(hookResults=o)
    finally:
        ws.stop()

    rc=None
    if hasattr(o,"rr"):
        toValid="%s:%s:%s" % (o.rr.ok,o.rr.total,o.rr.nbReqs)

        if valid:
            rc=0 if valid==toValid else 1
            print("Check valid:",valid,"?==",toValid,"-->",rc)
        else:
            print("No validation check! (valid:%s)" % toValid)

    return rc


if __name__=="__main__":
    sys.exit( main() )

