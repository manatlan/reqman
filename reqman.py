#!/usr/bin/python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2020 manatlan manatlan[at]gmail(dot)com
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

import os, sys, re, asyncio, io, datetime, itertools, glob, enum, codecs
import http, urllib, email  # for cookies management
import urllib.parse
import collections, json
import typing as T
import sys, traceback
import pickle, zlib, hashlib
import http.cookiejar
import concurrent, ssl
from xml.dom import minidom
import encodings.idna


# import httpcore # see "pip install httpcore"
import aiohttp  # see "pip install aiohttp"
import yaml  # see "pip install pyyaml"
import stpl  # see "pip install stpl"
import xpath  # see "pip install py-dom-xpath-six"

import jwt  # (pip install pyjwt) just for pymethods in rml files (useful to build jwt token)

# 95%: python3 -m pytest --cov-report html --cov=reqman .
__version__ = "2.6.0.0"  # only SemVer (the last ".0" is win only)
# bug fixes


try:  # colorama is optionnal
    from colorama import init, Fore, Style

    init()

    def colorize(color: int, t: str) -> T.Union[str, None]:
        return (
            color + Style.BRIGHT + str(t) + Fore.RESET + Style.RESET_ALL if t else None
        )

    cy = lambda t: colorize(Fore.YELLOW, t)
    cr = lambda t: colorize(Fore.RED, t)
    cg = lambda t: colorize(Fore.GREEN, t)
    cb = lambda t: colorize(Fore.CYAN, t)
    cw = lambda t: colorize(Fore.WHITE, t)
except ImportError:
    cy = cr = cg = cb = cw = lambda t: t

KNOWNVERBS = [
    "GET",
    "POST",
    "DELETE",
    "PUT",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "PATCH",
    "CONNECT",
]
KNOWNACTIONEXT = ["headers", "doc", "tests", "params", "foreach", "save", "body", "if"]
REQMAN_CONF = "reqman.conf"


class OutputConsole(enum.Enum):
    NO = 0
    MINIMAL = 1
    MINIMAL_ONLYKO = 2
    FULL = 3


class RMFormatException(Exception):
    pass


class RMException(Exception):
    pass


class RMPyException(Exception):
    pass


class RMNonResolvedVars(Exception):
    pass


def declare(code):
    return "def DYNAMIC(x,ENV):\n" + ("\n".join(["  " + i for i in code.splitlines()]))


def isPython(x):
    if type(x) == str and "return" in x:
        try:
            return compile(declare(x), "unknown", "exec") and True
        except:
            return False


def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)


def izip(ex1, ex2):
    pop = lambda ex: len(ex) > 0 and ex.pop(0) or None

    def trans(ex):
        tex = {}
        lex = []
        for i in ex:
            uid = i.id
            while uid in tex:
                uid += type(uid) == str and "b" or 1
            tex[uid] = i
            lex.append((uid, i))
        return tex, lex

    tex1, lex1 = trans(ex1)
    tex2, lex2 = trans(ex2)

    cex1 = [(i, tex2.get(uid)) for uid, i in lex1]
    cex2 = [(i, tex1.get(uid)) for uid, i in lex2]

    l = []
    while 1:
        i1 = pop(cex1)
        i2 = pop(cex2)
        if i1 is None and i2 is None:
            break
        if i1 == i2:
            l.append(i1)
        else:
            if i2 in cex1:
                l.append((i1[0], None))
                cex2.insert(0, i2)
            else:
                if i1 in cex2:
                    l.append((None, i2[0]))
                    cex1.insert(0, i1)
                else:
                    if i1:
                        l.append((i1[0], None))
                    if i2:
                        l.append((None, i2[0]))

    return [(e1, e2) for e1, e2 in l]


def comparable(l):
    for x1, x2 in l:
        return x1 == x2


def renameKeyInDict(d, oname, nname):
    for k, v in list(d.items()):
        if k == oname:
            d[nname] = d.pop(k)
        if isinstance(v, dict):
            renameKeyInDict(v, oname, nname)


def ustr(x):  # ensure str are utf8 inside
    # assert type(x)==str
    try:
        return x.encode("cp1252").decode()
    except:
        if type(x) == bytes:
            return x.encode("utf8").decode()
        else:
            return str(x)

def genKV(headers):
    for k, v in headers.items():
        if type(v) == list:  # cookies values (Set-Cookie) is possibly a list
            for i in v:
                yield (k, i)
        else:
            yield (k, v)


class CookieStore(http.cookiejar.CookieJar):  # TODO: can do a lot better with httpcore
    """ Manage cookiejar for httplib-like """

    def __init__(self, ll: T.List[dict] = []) -> None:
        http.cookiejar.CookieJar.__init__(self)
        for c in ll:
            self.set_cookie(http.cookiejar.Cookie(**c))

    def update(self, url: str, inHeaders: dict) -> dict:
        """return appended headers"""
        if url and url.lower().startswith("http"):
            r = urllib.request.Request(url)
            self.add_cookie_header(r)
            inHeaders.update(dict(r.header_items()))
            return dict(r.header_items())

    def extract(self, url: str, outHeaders: dict) -> None:
        if url and url.lower().startswith("http"):

            class FakeResponse(http.client.HTTPResponse):
                def __init__(self, headers=[], url=None) -> None:
                    """
                    headers: list of RFC822-style 'Key: value' strings
                    """
                    m = email.message_from_string("\n".join(headers))
                    self._headers = m
                    self._url = url

                def info(self):
                    return self._headers

            ll = ["%s: %s" % (k, v) for k, v in genKV(outHeaders)]

            self.extract_cookies(FakeResponse(ll, url), urllib.request.Request(url))

    def export(self) -> T.List[dict]:
        ll = []
        for i in self:
            ll.append(
                {
                    n if n != "_rest" else "rest": getattr(i, n)
                    for n in "version,name,value,port,port_specified,domain,domain_specified,domain_initial_dot,path,path_specified,secure,expires,discard,comment,comment_url,_rest".split(
                        ","
                    )
                }
            )
        return ll


def toStr(x):
    try:
        return x.decode()
    except:
        return str(x)


class Content:
    def __init__(self, content):
        self.__b = content if type(content) is bytes else ustr(content).encode()

    def __repr__(self) -> str:
        return toStr(self.__b)

    def toJson(self):
        try:
            return json.loads(self.__b.decode())
        except:
            return None

    def toXml(self):
        try:
            return Xml(repr(self))
        except:
            return None

    def __bytes__(self):
        return self.__b


class RmDict(dict):
    def __init__(self, **kargs):
        self.__dict__.update(kargs)
        dict.__init__(self, **kargs)


class HeadersMixedCase(dict):
    def __init__(self, **kargs):
        dict.__init__(self, **kargs)

    def __getitem__(self, key):
        d = {k.lower(): v for k, v in self.items()}
        return d.get(key.lower(), None)

    def get(self, key, default=None):
        d = {k.lower(): v for k, v in self.items()}
        return d.get(key.lower(), default)


"""
AHTTP = httpcore.AsyncClient(verify=False)

async def _request(method,url,body:bytes,headers, timeout=None):
    try:
        if (not body) and headers: headers["Content-Length"]="0"
        r = await AHTTP.request(
            method,
            url,
            data=body,
            headers=headers,
            allow_redirects=False,
            timeout=httpcore.TimeoutConfig( timeout ),
        )
        info = "%s %s %s" % (r.protocol, int(r.status_code), r.reason_phrase)
        return r.status_code, dict(r.headers), Content(r.content), info
    except (httpcore.exceptions.ReadTimeout, httpcore.exceptions.ConnectTimeout, httpcore.exceptions.Timeout, httpcore.exceptions.WriteTimeout):
        return None, {}, "Timeout", ""
    except OSError as e:
        return None, {}, "Unreachable", ""
    except httpcore.exceptions.InvalidURL:
        return None, {}, "Invalid", ""

async def request(method,url,body:bytes,headers, timeout=None):
    ''' mimic "_request()" to try 3 times, when Unreachable (to be really sure ;-) '''
    t = await _request(method,url,body,headers,timeout)
    if t[2]=="Unreachable": # conncetion lost, retry to see ;-)
        t = await _request(method,url,body,headers,timeout)
        if t[2]=="Unreachable": # conncetion lost, retry to see ;-)
            t = await _request(method,url,body,headers,timeout)
    return t
"""

textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
isBytes = lambda bytes: bool(bytes.translate(None, textchars))


async def request(method, url, body: bytes, headers, timeout=None):
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:

            r = await session.request(
                method,
                url,
                data=body,
                headers=headers,
                ssl=False,
                timeout=timeout,
                allow_redirects=False,
            )
            try:
                obj = await r.json()
                content = jdumps(obj).encode(
                    "utf-8"
                )  # ensure json chars are not escaped, and are in utf8
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
            outHeaders = dict(r.headers)
            if "Set-Cookie" in r.headers:
                outHeaders["Set-Cookie"] = list(r.headers.getall("Set-Cookie"))
            return r.status, outHeaders, Content(content), info
    except aiohttp.client_exceptions.ClientConnectorError as e:
        return None, {}, "Unreachable", ""
    except concurrent.futures._base.TimeoutError as e:
        return None, {}, "Timeout", ""
    except aiohttp.client_exceptions.InvalidURL as e:
        return None, {}, "Invalid", ""
    except ssl.SSLError:
        pass


class FString(str):
    filename = None
    encoding = None

    def __new__(cls, fn: str):
        for e in ["utf8", "cp1252"]:
            try:
                with io.open(fn, "r", encoding=e) as fid:
                    obj = str.__new__(cls, fid.read())
                    obj.filename = fn
                    obj.encoding = e
                    return obj
            except UnicodeDecodeError:
                pass
        raise Exception("Can't read '%s'" % fn)


clone = lambda x: json.loads(json.dumps(x))


def toList(d) -> T.List:
    return d if type(d) == list else [d]


padLeft = lambda b: ("\n".join(["  " + i for i in str(b).splitlines()]))


def dict_merge(dst: dict, src: dict) -> None:
    """ merge dict 'src' in --> dst """
    for k, v in src.items():
        if (
            k in dst
            and isinstance(dst[k], dict)
            and isinstance(src[k], collections.abc.Mapping)
        ):
            dict_merge(dst[k], src[k])
        else:
            if k in dst and isinstance(dst[k], list) and isinstance(src[k], list):
                dst[k] += src[k]
            else:
                dst[k] = src[k]


class NotFound:
    pass


def DYNAMIC(x, env: dict) -> T.Union[str, None]:
    pass  # will be overriden (see below vv)


def jpath(elem, path: str) -> T.Union[int, T.Type[NotFound], str]:
    orig = Env(elem)
    for i in path.strip(".").split("."):
        try:
            if type(elem) == list:
                if i == "size":
                    return len(elem)
                else:
                    elem = elem[int(i)]
            elif isinstance(elem, dict):
                if i == "size":
                    return len(list(elem.keys()))
                else:
                    elem = elem.get(i, NotFound)

                    if isPython(elem):
                        elem = orig.transform(None, i)

            elif type(elem) == str:
                if i == "size":
                    return len(elem)
        except (ValueError, IndexError) as e:
            return NotFound
    return elem


def xj(xp):
    """
  Split xpath/jpath expr in -> xpath,jpath
  ex:   "//b[@v='.'].-1.size" ---> ( "//b[@v='.']" , '-1.size' )
  """
    ll = xp.split(".")
    if len(ll) > 1:
        ends = []
        while 1:
            if "size" in ll[-1]:
                ends.append(ll.pop())
            elif ll[-1].lstrip("-+").isdigit():
                ends.append(ll.pop())
            else:
                break
        return ".".join(ll), ".".join(reversed(ends))
    else:
        return xp, ""


class Xml:
    def __init__(self, x):
        self.doc = minidom.parseString(x)

    def xpath(self, p):
        ll = []
        for ii in xpath.find(p, self.doc):
            if ii.nodeType in [self.doc.ELEMENT_NODE, self.doc.DOCUMENT_NODE]:
                ll.append(xpath.expr.string_value(ii))
            elif ii.nodeType == self.doc.TEXT_NODE:
                ll.append(ii.wholeText)
            elif ii.nodeType == self.doc.ATTRIBUTE_NODE:
                ll.append(ii.value)
            else:  # 'CDATA_SECTION_NODE', 'COMMENT_NODE', 'DOCUMENT_FRAGMENT_NODE', 'DOCUMENT_TYPE_NODE', 'ENTITY_NODE', 'ENTITY_REFERENCE_NODE', 'NOTATION_NODE', 'PROCESSING_INSTRUCTION_NODE'
                raise Exception("Not implemented")

        if ll:
            return ll
        else:
            return NotFound

    def __repr__(self):
        xml = self.doc.toprettyxml(indent=" " * 4)
        x = "\n".join(
            [s for s in xml.splitlines() if s.strip()]
        )  # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/
        return x


class Exchange:
    def __init__(
        self,
        method,
        path,
        url,
        body,
        inHeaders,
        status,
        outHeaders,
        content,
        info,
        time,
    ):
        self.id = None
        self.doc = None
        self.scope = None
        self.tests = []
        self.nolimit = False

        self.method = method
        self.path = path
        self.url = url
        self.body = body
        self.bodyContent = Content(body)
        self.inHeaders = HeadersMixedCase(**inHeaders)
        self.status = status
        self.outHeaders = HeadersMixedCase(**outHeaders)
        self.content = content
        self.info = info
        self.time = time

    def __eq__(self, o):
        return o and self.id == o.id

    def __repr__(self):
        return "<Exchange: %s %s -> %s tests:%s>" % (
            self.method,
            self.url,
            self.status,
            self.tests or "no",
        )


class Env(dict):
    path=None

    def __init__(self, d=None, path=None):
        self.path=path and os.path.dirname(path) or None
        if not d:
            d = {}

        if isinstance(d, str):
            d = ustr(d)
            try:
                d = yaml.load(d, Loader=yaml.FullLoader)
            except Exception as e:
                raise RMFormatException("Env conf is not yaml")

        if type(d) not in [dict, Env]:
            # raise RMFormatException("Env conf is not a dict %s" % str(d))
            d = {}

        self.__shared = {}  # shared saved scope between all cloned Env
        self.__global = (
            {}
        )  # shared global saved scope between all cloned Env (from BEGIN only)

        dict.__init__(self, dict(d))
        self.cookiejar = CookieStore()

    def _getProc(self, name):
        return Reqs(yaml.dump(self[name]) if name in self else "", self, name=name)

    def getBEGIN(self, local=False):
        if local:
            return self._getProc(".BEGIN")
        else:
            return self._getProc("BEGIN")

    def getEND(self, local=False):
        if local:
            return self._getProc(".END")
        else:
            return self._getProc("END")

    def save(self, key, value, isGlobal=False):
        self[key] = value
        self.__shared[key] = value
        if isGlobal:
            self.__global[key] = value

    def clone(self, cloneSharedScope=True):
        newOne = Env({})
        dict_merge(newOne, self)
        newOne.cookiejar = CookieStore(self.cookiejar.export())

        dict_merge(
            newOne, self.__global
        )  # declare those of the global scope !!! (from BEGIN only)
        newOne.__global = self.__global  # mk a ref to global

        if (
            cloneSharedScope
        ):  # used (at false) at each Reqs() constructor (to start on a sane base)
            dict_merge(newOne, self.__shared)  # declare those of the shared scope !!!
            newOne.__shared = self.__shared  # mk a ref to shared
        newOne.path=self.path
        return newOne

    @property
    def switches(self):
        """ return list of tuple (switchName,doc) """
        if "switches" in self.keys():
            # new system (hourraaaaa !!!! )
            switches = self["switches"].keys()
            for k in switches:
                yield k, self["switches"].get(k, {}).get("doc", "???")
        elif "switchs" in self.keys():
            # new system (but with bad name)
            switches = self["switchs"].keys()
            for k in switches:
                yield k, self["switchs"].get(k, {}).get("doc", "???")
        else:
            # old system #DEPRECATED
            for k, v in self.items():
                root = v.get("root", None) if type(v) == dict else None
                if root:
                    yield (
                        k,
                        v.get("doc", root),
                    )  # return the doc or the url of the root

    def mergeSwitch(self, switch):
        if switch in self:  # DEPRECATED
            dict_merge(self, self[switch])
        else:
            switches = self.get("switches", {})
            if not switches:
                switches = self.get("switchs", {})
            if switch in switches:
                dict_merge(self, switches[switch])

    def replaceObj(
        self, v: T.Any
    ) -> T.Any:  # same as txtReplace() but for "object" (json'able)
        if type(v) is bytes:
            return v
        elif type(v) is Content:  # (when save to var)
            return bytes(v)
        elif type(v) is not str:
            v = jdumps(v)

        obj = self.replaceTxt(v)
        if type(obj) is bytes:
            return obj
        else:
            try:
                obj = json.loads(obj)
            except (json.decoder.JSONDecodeError, TypeError):
                pass
            return obj

    def replaceObjOrNone(
        self, v: T.Any
    ) -> T.Any:  # same as txtReplace() but for "object" (json'able)
        v = self.replaceObj(v)
        return v if self.getNonResolvedVars(v) == [] else None

    def getNonResolvedVars(self, txt):
        if type(txt) == str:
            return re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt)
        else:
            return []

    def replaceTxt(self, txt: str) -> T.Union[str, bytes]:
        assert type(txt) is str

        def _replace(txt: str) -> T.Union[str, bytes]:
            def getVar(var: str):
                methods = re.findall(r"\|[\d\w\|]+$", var)
                if methods:
                    p = var.index(methods[0])
                    key = var[:p]
                    method = var[p + 1 :]

                    content = getVar(key)
                    if content is NotFound:
                        content = None

                    for m in method.split("|"):
                        if (
                            type(content) != RmDict
                        ):  # No try to replace things on a RmDict
                            content = self.replaceObj(
                                content
                            )  ## important, resolv inner method first .... see tests 044, 045, 046

                        content = self.transform(content, m)
                    return content
                elif "." in var:
                    # -(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(
                    vx, xp = var.split(".", 1)
                    if vx in self and type(self[vx]) is Xml:

                        xp, ends = xj(xp)

                        ll = self[vx].xpath(xp)
                        if type(ll) == list and ends:
                            return jpath(ll, ends)
                        else:
                            return ll
                    elif vx in self and type(self[vx]) == str:
                        s = self[vx]
                        if s.startswith("<<") and s.endswith(">>"):
                            content = self.replaceObj(s)
                            return jpath(content, xp)
                    # -(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(-(
                    return jpath(self, var)

                elif var in self:
                    if isPython(self[var]):
                        return self.transform(None, var)
                    else:
                        return self[var]
                else:
                    return NotFound

            for vvar in self.getNonResolvedVars(txt):
                var = vvar[2:-2]

                val = getVar(var)

                if val is not NotFound:
                    if type(val) != str:
                        if val is None:
                            val = "null"
                        elif val is True:
                            val = "true"
                        elif val is False:
                            val = "false"
                        elif type(val) == bytes:
                            return val  # keep BYTES !!!!!!!!!!!!!!
                        else:  # int, float, list, dict...
                            try:
                                val = jdumps(val)
                            except TypeError:
                                val = str(val)

                        txt = txt.replace('"%s"' % vvar, val)
                    else:
                        txt = txt.replace('"%s"' % vvar, '"%s"' % val)

                    txt = txt.replace(vvar, val)

            return txt

        while type(txt) is str:
            _txt = _replace(txt)
            if _txt == txt:  # no change ... it's time to return ;-)
                return txt
            else:
                txt = _txt
        return txt  # bytes

    def transform(
        self, content: T.Union[str, None], methodName: str
    ) -> T.Union[str, None]:
        if methodName:
            if methodName in self:
                code = self[methodName]
                try:
                    exec(declare(code), globals())
                except Exception as e:
                    raise RMPyException(
                        "Error in declaration of method " + methodName + " : " + str(e)
                    )

                if content is None:
                    x = None
                elif type(content) == str:
                    try:
                        x = json.loads(content)
                    except (json.decoder.JSONDecodeError, TypeError):
                        x = content
                else:
                    x = content

                try:
                    content = DYNAMIC(x, self)
                except Exception as e:
                    raise RMPyException(
                        "Error in execution of method " + methodName + " : " + str(e)
                    )
            else:
                raise RMPyException("Can't find method '%s'" % methodName)

        return content

    def __str__(self):
        return jdumps(self, indent=4, sort_keys=True)

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.__dict__ = state
        self.__shared = {}
        self.__global = {}
        self.cookiejar = CookieStore()


class Reqs(list):
    def __init__(
        self, obj: T.Union[str, FString], env=None, trace=False, name="<YamlString>"
    ):
        self.__proc = {}
        self._trace = trace
        self.exchanges = None  # list of Exchange
        self.name = obj.filename if type(obj) is FString else name

        if env is None:
            self.env = Env()
        elif type(env) is Env:
            self.env = env.clone(cloneSharedScope=False)  # remove shared one
        elif type(env) is dict:
            self.env = Env(env)

        def controle(obj) -> T.List:
            """ Controle that 'obj' is a list of dict, and is valid """
            if type(obj) == list:
                pass
            elif type(obj) == dict:
                obj = toList(obj)
            elif obj is None:
                obj = []
            else:
                raise self._errorFormat("Reqs: bad object content")
            # here 'obj' is a list of dict

            liste = []
            for i in obj:
                if isinstance(i, str):
                    if i == "break":
                        print(cy("**WARNING**"), "a", cr("break"), "in", self.name)
                        break
                    else:
                        raise self._errorFormat("Reqs: Unknown action '%s'" % i)
                elif isinstance(i, dict):
                    keys = list(i.keys())
                    if (
                        len(keys) == 1
                        and (keys[0] not in KNOWNVERBS + ["call"])
                        and (type(i[keys[0]]) in [dict, list])
                    ):

                        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ SELFCONF
                        if "conf" in keys:
                            s = i["conf"]
                            self._assertType("conf", s, [dict])

                            if any([type(i) is ReqConf for i in liste]):
                                raise self._errorFormat(
                                    "Reqs: multiple 'conf' (only one is possible)"
                                )

                            liste.insert(0, ReqConf(s))
                            continue
                        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ SELFCONF

                        # it's a definition of a proc's named 'key', content = value
                        key = keys[0]
                        value = i[key]
                        if key in self.__proc:
                            raise self._errorFormat(
                                "Reqs: multiple proc are named '%s'" % key
                            )

                        # declare the proc in the scope
                        self.__proc[key] = value

                    else:
                        foreach = i.get("foreach", None)
                        self._assertType("foreach", foreach, [list, str])

                        scopeParams = i.get("params", {})
                        self._assertType("params", scopeParams, [dict])

                        if "call" in keys:
                            call = i["call"]
                            self._assertType("call", call, [list, str])
                            if not all([k in KNOWNACTIONEXT + ["call"] for k in keys]):
                                raise self._errorFormat(
                                    "Reqs: There are keys that are not understandable %s"
                                    % ",".join(keys)
                                )

                            for namedProc in toList(call):

                                # TODO: test not dynamic (not call: <<proc>>) !

                                if namedProc in self.__proc:
                                    reqs = controle(self.__proc[namedProc])
                                elif namedProc in self.env:
                                    reqs = controle(self.env[namedProc])
                                else:
                                    raise self._errorFormat(
                                        "Reqs: call a proc '%s' that doesn't exist"
                                        % namedProc
                                    )

                                for r in reqs:  # surcharge reqs from 'i'
                                    r.updateIf(i)
                                    r.updateBody(i)
                                    r.updateDoc(i)
                                    r.updateHeaders(i)
                                    r.updateSave(i)
                                    r.updateTests(i)

                                liste.append(ReqGroup(reqs, foreach, scopeParams))

                        elif any([v in keys for v in KNOWNVERBS]):
                            # there is a KNOWNVERBS's action in the dict 'i'
                            verbs = list(set(KNOWNVERBS).intersection(list(keys)))
                            if len(verbs) > 1:
                                raise self._errorFormat(
                                    "Reqs: There are too many http verb in this action %s"
                                    % ",".join(verbs)
                                )

                            if not all(
                                [k in KNOWNACTIONEXT + KNOWNVERBS for k in keys]
                            ):
                                raise self._errorFormat(
                                    "Reqs: There are keys that are not understandable %s"
                                    % ",".join(keys)
                                )

                            # append the current action/req to the liste
                            method = verbs[0]
                            path = i.get(method, None)
                            if type(path) is not str:
                                raise self._errorFormat(
                                    "Reqs: The action %s should contains a path/string"
                                    % method
                                )

                            r = Req(method, path, self)
                            r.updateIf(i)
                            r.updateBody(i)
                            r.updateDoc(i)
                            r.updateHeaders(i)
                            r.updateSave(i)
                            r.updateTests(i)

                            if foreach is None:  # no foreach
                                r.updateParams(i)
                                liste.append(r)
                            else:  # foreach
                                liste.append(ReqGroup([r], foreach, scopeParams))
                        else:
                            raise self._errorFormat(
                                "Reqs: unknown action in %s" % ", ".join(keys)
                            )
                else:
                    raise self._errorFormat("Reqs: bad object %s" % i)

            return liste

        if isinstance(obj, str):
            obj = ustr(obj)
            try:
                y = yaml.load(obj, Loader=yaml.FullLoader)
            except Exception as e:
                raise self._errorFormat("Reqs: YML syntax in %s\n%s" % (self.name, e))

            lreqs = controle(y)
        else:
            raise self._errorFormat("Reqs: bad object")

        # here 'obj' is a list of ReqBase, and valid one
        list.__init__(self, lreqs)
        if self._trace:
            print("~" * 80)
            print("~~ Reqs")
            print("~" * 80)
            print("env:", self.env)
            print(self)
            print("~" * 80)

    def _errorFormat(self, msg):
        return RMFormatException(msg + " in %s" % self.name)

    def _assertType(self, name, o, types):
        if o is not None and type(o) not in types:
            raise self._errorFormat("TT: %s is malformed, not a %s" % (name, types))

    def execute(self, http=None, outputConsole=OutputConsole.MINIMAL) -> list:
        """ call asyncReqsExecute in sync, used only in old pytests """
        switches = []
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.asyncReqsExecute(switches, http, outputConsole=outputConsole)
        )

    async def asyncReqsExecute(
        self, switches: list, http=None, outputConsole=OutputConsole.MINIMAL
    ) -> list:
        assert type(switches) is list
        ############################################# live console
        if len(self) > 0 and outputConsole in [
            OutputConsole.MINIMAL,
            OutputConsole.FULL,
        ]:
            print("TEST:", cb(self.name))
        ############################################# live console

        def log(level, *l):
            if self._trace:
                print(level * "    ", " ".join([str(x) for x in l]))

        log(0, "~" * 80)
        log(0, "~~ Reqs.Execute")
        log(0, "~" * 80)

        def oneline(s):
            return str(s).splitlines()

        def _test(liste: Reqs, gscope, level=0):
            log(level, "Test Global Scope :", gscope)

            for idx, i in enumerate(liste):
                if isinstance(i, Req):
                    log(level, "* Req:", oneline(i))
                    yield level, gscope, i.clone()  # this clone has no effect ;-)

                elif isinstance(i, ReqGroup):
                    scope = gscope.clone()  # important

                    log(level, "* ReqGroup:", len(i.reqs), "ReqItem(s)")

                    dict_merge(scope, i.scope)
                    log(level, "  Scope Add: ", i.scope)

                    foreach = i.foreach or [{}]
                    if type(foreach) == str:  # dynamic foreach !
                        try:
                            foreach = json.loads(scope.replaceTxt(foreach))
                        except json.decoder.JSONDecodeError as e:
                            raise RMException(
                                "Reqs: Dynamic foreach '%s' is not a list of dict"
                                % foreach
                            )
                        except RMPyException as e:
                            raise RMException("Reqs: Dynamic foreach ERROR %s" % e)

                        if type(foreach) != list or any(
                            [type(p) != dict for p in foreach]
                        ):
                            raise RMException(
                                "Reqs: Dynamic foreach params is not a list of dict"
                            )

                    for fparam in foreach:
                        log(level, "  Foreach with params:", fparam)

                        for l, s, r in _test(i.reqs, scope, level + 1):
                            r.updateParams({"params": fparam})
                            yield l, s, r
                elif isinstance(i, ReqConf):
                    pass  # already treated !
                else:
                    raise RMException("Reqs: unwaited object %s" % i)

        gscope = self.env.clone()

        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ SELFCONF
        ll = []
        for i in self:
            if isinstance(i, ReqConf):
                print(cy("**WARNING**"), "%s use self conf" % self.name)

                localEnv = Env(i.conf)
                for switch in switches:
                    localEnv.mergeSwitch(switch)

                gscope.update(dict(localEnv))

        reqsBegin = gscope.getBEGIN(local=True)
        reqsEnd = gscope.getEND(local=True)
        if reqsBegin is not None:
            for r in reqsBegin:
                ll.append(
                    await r.asyncReqExecute(gscope, http, outputConsole=outputConsole)
                )
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        for l, s, r in _test(self, gscope):
            doIf = True
            if r.ifs:
                envIf = s.clone()
                dict_merge(envIf, r.params)
                doIf = all([envIf.replaceObjOrNone(i) for i in r.ifs])

            if doIf:
                ex = await r.asyncReqExecute(s, http, outputConsole=outputConsole)
                ll.append(ex)
                log(l, "  >>> EXECUTE:", ex)

        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ SELFCONF
        if reqsEnd is not None:
            for r in reqsEnd:
                ll.append(
                    await r.asyncReqExecute(gscope, http, outputConsole=outputConsole)
                )
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        self.exchanges = ll
        return ll

    def __repr__(self):
        return "\n".join(["Reqs's Name: %s" % self.name] + [repr(i) for i in self])


class ReqItem:
    pass


class ReqConf(ReqItem):
    def __init__(self, conf: dict):

        conf = clone(conf)
        renameKeyInDict(conf, "BEGIN", ".BEGIN")
        renameKeyInDict(conf, "END", ".END")

        self.conf = conf

    def __repr__(self):
        return "<ReqConf %s>" % self.conf


class ReqGroup(ReqItem):
    def __init__(self, reqs: list, foreach, params):
        self.reqs = reqs
        self.foreach = foreach
        self.scope = params

    def updateIf(self, o: dict):
        for r in self.reqs:
            r.updateIf(o)

    def updateHeaders(self, o: dict):
        for r in self.reqs:
            r.updateHeaders(o)

    def updateTests(self, o: dict):
        for r in self.reqs:
            r.updateTests(o)

    def updateBody(self, o: dict):
        for r in self.reqs:
            r.updateBody(o)

    def updateDoc(self, o: dict):
        for r in self.reqs:
            r.updateDoc(o)

    def updateSave(self, o: dict):
        for r in self.reqs:
            r.updateSave(o)

    def __repr__(self):
        l = []
        l.append("<ReqGroup foreach:%s scope:%s>" % (self.foreach, self.scope))
        for i in self.reqs:
            l.append(padLeft(str(i)))
        return "\n".join(l)


class Req(ReqItem):
    def __init__(self, method: str, path: str, parent: Reqs):
        assert method in KNOWNVERBS
        if path.startswith("+"):
            path = path[1:]
            self.nolimit = True
        else:
            self.nolimit = False
        self.parent = parent
        self.method = method
        self.path = path

        self.headers = {}
        self.params = Env()
        self.tests = []
        self.body = None  # or str,dict,list,bool,bytes,int,float
        self.doc = None  # or str
        self.saves = []
        self.ifs = []

    def clone(self):
        r = Req(self.method, self.path, self.parent)
        r.headers = clone(self.headers)
        r.params = clone(self.params)
        r.tests = clone(self.tests)
        r.body = clone(self.body)
        r.doc = clone(self.doc)
        r.saves = clone(self.saves)
        r.nolimit = clone(self.nolimit)
        r.ifs = clone(self.ifs)
        return r

    def updateIf(self, o: dict):  # merge headers
        if "if" in o:
            v = o.get("if", None)
            self.parent._assertType("if", v, [str, int, bool, float])
            self.ifs.append(v)

    def updateHeaders(self, o: dict):  # merge headers
        headers = o.get("headers", {})
        self.parent._assertType("headers", headers, [dict, list])
        if type(headers) is list:  # list > dict
            # TODO: "'headers:' should be filled of key/value pairs (ex: 'Content-Type: text/plain')"
            headers = {list(d.keys())[0]: list(d.values())[0] for d in headers}
        if headers is not None:
            dict_merge(self.headers, headers)

    def updateParams(self, o: dict):  # merge params
        params = o.get("params", {})
        self.parent._assertType("params", params, [dict])
        if params is not None:
            dict_merge(self.params, params)

    def updateTests(self, o: dict):  # append tests
        tests = o.get("tests", [])
        self.parent._assertType("tests", tests, [list, dict])
        if type(tests) == dict:  # dict to list
            # TODO: "'tests:' should be a list of mono key/value pairs (ex: '- status: 200')"
            tests = [{k: v} for k, v in dict(tests).items()]
        if tests is not None:
            self.tests += tests

    def updateBody(self, o: dict):  # replace body
        body = o.get("body", None)
        self.parent._assertType(
            "body", body, [str, dict, list, bool, bytes, int, float]
        )
        if body is not None:
            self.body = body

    def updateDoc(self, o: dict):  # replace doc
        doc = o.get("doc", None)
        self.parent._assertType("doc", doc, [str])
        if doc is not None:
            self.doc = doc

    def updateSave(self, o: dict):  # append save
        save = o.get("save", None)
        self.parent._assertType("save", save, [str, dict])  # new
        if type(save) is str:
            save = {save: "<<content>>"}  # convert to new system save
        if save is not None:
            self.saves += [save]

    def __repr__(self):
        l = []
        l.append("<Req %s: %s>" % (self.method, self.path))
        if self.ifs:
            l.append("\tif: %s" % (self.ifs))
        if self.headers:
            l.append("\theaders: %s" % (self.headers))
        if self.params:
            l.append("\tparams: %s" % (self.params))
        if self.tests:
            l.append("\ttests: %s" % (self.tests))
        if self.body:
            l.append("\tbody: %s" % (self.body))
        if self.doc:
            l.append("\tdoc: %s" % (self.doc))
        if self.saves:
            l.append("\tsaves: %s" % (self.saves))
        return "\n".join(l)

    async def asyncReqExecute(
        self, gscope, http=None, outputConsole=OutputConsole.MINIMAL
    ) -> Exchange:
        scope = gscope.clone()  # important
        dict_merge(scope, self.params)

        root = scope.get("root", None)  # global root
        gheaders = scope.get("headers", None)  # global header
        try:
            timeout = scope.get("timeout", None)  # global timeout
            timeout = timeout and float(timeout) / 1000.0 or None
        except ValueError:
            timeout = None

        method, path, body, headers = self.method, self.path, self.body, self.headers
        doc, tests, saves = self.doc, self.tests, self.saves

        #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' compute an unique id based on reqs's attributes
        uid = hashlib.md5()
        uid.update(
            json.dumps([method, path, body, headers, doc, tests, saves]).encode()
        )
        #''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        gpath = path
        ex = None
        try:

            def resolvHeaders(headers):
                if type(headers) == str:
                    headers = scope.replaceObj(headers)
                self.parent._assertType("headers", headers, [dict, list])
                return headers

            if gheaders is not None:
                newHeaders = resolvHeaders(clone(gheaders))
                dict_merge(newHeaders, headers)
                headers = newHeaders

            path = scope.replaceTxt(path)

            if root is not None and not urllib.parse.urlparse(path.lower()).scheme:
                url = scope.replaceTxt(root) + path
            else:
                url = path

            if body:
                body = scope.replaceObj(body)

            headers = resolvHeaders(headers)
            headers = {
                k: scope.replaceTxt(str(v)) for k, v in headers.items() if v
            }  # headers'value should be string

            # #=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ test if all vars are resolved
            if scope.getNonResolvedVars(path):
                raise RMNonResolvedVars("`Path` non resolved")
            if scope.getNonResolvedVars(body):
                raise RMNonResolvedVars("`Body` non resolved")
            for k, v in headers.items():
                if scope.getNonResolvedVars(v):
                    raise RMNonResolvedVars("Header `%s` non resolved" % k)
            # =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+

            tests = [
                {list(d.keys())[0]: scope.replaceObj(list(d.values())[0])}
                for d in tests
            ]  # cast value as str

            # set cookies in request according env
            self.parent.env.cookiejar.update(url, headers)

            ex = await asyncExecute(
                method, gpath, url, body, headers, http=http, timeout=timeout
            )
        except (
            RMPyException,
            RMFormatException,
            RMNonResolvedVars,
        ) as e:  # RMFormatException for headers resolver !
            ex = Exchange(
                method,
                gpath,
                gpath,
                body or "",
                headers,
                None,
                {},
                str(e),
                "TEST EXCEPTION",
                0,
            )
        except Exception as e:  # RMFormatException for headers resolver !
            ex = Exchange(
                method,
                gpath,
                gpath,
                body or "",
                headers,
                500,
                {},
                str(e),
                "TEST EXCEPTION (bug)",
                0,
            )
        finally:
            assert ex
            self.parent.env.cookiejar.extract(ex.url, ex.outHeaders)

        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        envResponse = scope.clone()
        contentAsJson = ex.content.toJson() if type(ex.content) == Content else None
        contentAsXml = ex.content.toXml() if type(ex.content) == Content else None

        envResponse["request"] = RmDict(  # new
            path=ex.url,
            method=ex.method,
            content=ex.bodyContent,  # Content type
            headers=ex.inHeaders,  # HeadersMixedCase type
        )
        envResponse["response"] = RmDict(  # new
            status=ex.status,
            content=ex.content,  # Content type
            headers=ex.outHeaders,  # HeadersMixedCase type
            time=ex.time,
        )

        envResponse["rm"] = RmDict(
            response=envResponse["response"], request=envResponse["request"]
        )

        # shorhands (historik)
        envResponse["content"] = envResponse["response"]["content"]
        envResponse["status"] = envResponse["response"]["status"]
        envResponse["headers"] = envResponse["response"]["headers"]

        if contentAsJson:
            envResponse["response"]["json"] = contentAsJson
            envResponse["json"] = contentAsJson  # shothands (historik)

        if contentAsXml:
            envResponse["response"]["xml"] = contentAsXml
            envResponse["xml"] = contentAsXml  # shothands (historik)

        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

        try:  # postsave
            for s in saves:
                for saveKey, saveWhat in s.items():
                    v = envResponse.replaceObj(saveWhat)
                    self.parent.env.save(saveKey, v, self.parent.name == "BEGIN")
                    envResponse[saveKey] = v
        except RMPyException as e:
            ex.status = None
            ex.content = e
            ex.info = "SAVE EXCEPTION"

            # important ! (not top ;-( )
            envResponse["content"] = ex.content
            envResponse["status"] = ex.status
            envResponse["response"]["content"] = ex.content
            envResponse["response"]["status"] = ex.status
            envResponse["rm"]["response"]["content"] = ex.content
            envResponse["rm"]["response"]["status"] = ex.status

        # upgrade 'ex' !
        ex.id = uid.hexdigest()
        ex.doc = envResponse.replaceTxt(doc) if doc else None
        ex.scope = scope
        ex.nolimit = self.nolimit
        ex.tests = TestResult(tests, envResponse, ex.status)

        # =================================================== LIVE CONSOLE
        if outputConsole != OutputConsole.NO:
            allIsOk = all(ex.tests)
            if not (allIsOk and outputConsole == OutputConsole.MINIMAL_ONLYKO):
                print(
                    "*",
                    cy(ex.method),
                    ex.url,
                    "-->",
                    cw(ex.content if ex.status is None else ex.status),
                )

                if outputConsole == OutputConsole.FULL:
                    display = lambda h: "\n".join(["%s: %s" % (k,v) for k,v in genKV(h)])

                    if ex.inHeaders:
                        print(padLeft(display(ex.inHeaders)))
                    if ex.body:
                        print(padLeft(ex.bodyContent))
                    print(padLeft("-" * 75))
                    if ex.outHeaders:
                        print(padLeft(display(ex.outHeaders)))
                    if ex.content:
                        print(padLeft(ex.content))
                    print(padLeft("-" * 75))

                for t in ex.tests:
                    if ex.status is None:
                        print("  -", t and "OK" or "KO", ":", t.name)
                    else:
                        print("  -", t and cg("OK") or cr("KO"), ":", t.name)
                print()
        # =================================================== LIVE CONSOLE

        return ex


async def asyncExecute(
    method, path, url, body, headers, http=None, timeout=None
) -> Exchange:
    t1 = datetime.datetime.now()

    if type(body) is not bytes:
        if body is None:
            body = "".encode()
        elif type(body) is str:
            body = body.encode()
        else:
            body = jdumps(body).encode()

    if type(http) == dict:
        status, content, outHeaders, info = (
            404,
            "mock not found",
            {"server": "reqman mock"},
            "MOCK RESPONSE",
        )
        if url in http:
            rep = http[url]
            if callable(rep):
                rep = rep(method, url, body, headers)

            if len(rep) == 2:
                status, content = rep
            elif len(rep) == 3:
                status, content, oHeaders = rep
                dict_merge(outHeaders, oHeaders)
            else:
                status, content = 500, "mock server error"
            assert type(content) in [str, bytes]
            assert type(status) is int
            assert type(outHeaders) is dict
        content = Content(content)
    else:
        http = request  # use the real one !!
        status, outHeaders, content, info = await http(
            method, url, body, headers, timeout=timeout
        )

    diff = datetime.datetime.now() - t1
    time = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
    return Exchange(
        method, path, url, body, headers, status, outHeaders, content, info, time
    )


######################################################################################"
## test part (old code)
######################################################################################"
class Test(int):
    """ a boolean with a name """

    name = ""

    def __init__(self, v, n1, n2, realValue):
        pass  # just for mypy

    def __new__(
        cls, value: int, nameOK: str = None, nameKO: str = None, realValue=None
    ):
        s = super().__new__(cls, value)
        if value:
            s.name = nameOK
        else:
            s.name = nameKO
        s.value = realValue
        return s

    def __repr__(self):
        return "%s: %s" % ("OK" if self else "KO", self.name)


def strjs(x) -> str:
    if type(x) is bytes:
        return str(x)
    elif type(x) is str:
        return x
    else:
        return jdumps(x)


def guessValue(txt):
    if type(txt) == str:
        try:
            return json.loads(txt)
        except:
            try:
                return json.loads('"%s"' % txt.replace('"', '\\"'))
            except:
                return txt
    return txt


def getValOpe(v):
    try:
        if type(v) == str and v.startswith("."):
            g = re.match(r"^\. *([\?!=<>]{1,2}) *(.+)$", v)
            if g:
                op, v = g.groups()
                if op in ["==", "="]:  # not needed really, but just for compatibility
                    return v, lambda a, b: b == a, "=", "!="
                elif op == "!=":
                    return v, lambda a, b: b != a, "!=", "="
                elif op == ">=":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b >= a or False,
                        ">=",
                        "<",
                    )
                elif op == "<=":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b <= a or False,
                        "<=",
                        ">",
                    )
                elif op == ">":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b > a or False,
                        ">",
                        "<=",
                    )
                elif op == "<":
                    return (
                        v,
                        lambda a, b: b != None and a != None and b < a or False,
                        "<",
                        ">=",
                    )
                elif op == "?":
                    return (
                        v,
                        lambda a, b: str(a) in str(b),
                        "contains",
                        "doesn't contain",
                    )
                elif op in ["!?", "?!"]:
                    return (
                        v,
                        lambda a, b: str(a) not in str(b),
                        "doesn't contain",
                        "contains",
                    )
    except (
        yaml.scanner.ScannerError,
        yaml.constructor.ConstructorError,
        yaml.parser.ParserError,
    ):
        pass
    return v, lambda a, b: a == b, "=", "!="


# def lowerIfHeader(t:str):
#     if t.startswith("headers."):
#         tt=t.split("|",1)
#         t="|".join( [tt[0]] + tt[1:] )
#     return t


class TestResult(list):
    def __init__(self, tests, env, status) -> None:

        results = []
        for test in tests:
            what, value = list(test.keys())[0], list(test.values())[0]
            # tvalue=env.replaceObjOrNone("<<%s>>" % lowerIfHeader(what))
            tvalue = env.replaceObjOrNone("<<%s>>" % what)

            firstWord = re.split(r"[\.|]", what)[0]
            testContains = False  # true pour content & "old headers" !!!!!
            # to ensure compatibility with < 2.3.8
            if firstWord == "content":
                testContains = True
            elif firstWord == "status":
                testContains = False
            elif firstWord == "json":
                testContains = False
            elif firstWord == "xml":
                testContains = False
            elif firstWord == "headers":
                testContains = False
            else:  # header
                if "headers" in env:
                    v = env["headers"][what]
                    if v:
                        print(
                            cy("**DEPRECATED**"),
                            "use new header syntax in tests (- headers.%s: ...)" % what,
                        )
                        tvalue = v
                        testContains = True

            # test if all match as json (list, dict, str ...)
            try:

                def makeComparable(x):
                    if type(x) is bytes:
                        return x
                    else:
                        return jdumps(
                            json.loads(x) if type(x) in [str, bytes] else x,
                            sort_keys=True,
                        )

                matchAll = makeComparable(value) == makeComparable(tvalue)
            except json.decoder.JSONDecodeError as e:
                matchAll = False

            if matchAll:
                test, opOK, opKO, val = True, "=", "!=", value
            else:
                # ensure that we've got a list
                values = [value] if type(value) != list else value
                opOK, opKO = None, None
                bool = False

                for value in values:  # match any
                    if testContains:
                        value, ope, opOK, opKO = (
                            value,
                            lambda x, c: toStr(x) in toStr(c),
                            "contains",
                            "doesn't contain",
                        )
                    else:
                        value, ope, opOK, opKO = getValOpe(value)

                    try:
                        bool = ope(guessValue(value), guessValue(tvalue))
                    except TypeError:
                        bool = False
                    if bool:
                        break

                bool = bool and status != None  # make test KO if status is invalid

                if len(values) == 1:
                    test, opOK, opKO, val = bool, opOK, opKO, value
                else:
                    test, opOK, opKO, val = (bool, "in", "not in", values)

            nameOK = what + " " + opOK + " " + strjs(val)  # test name OK
            nameKO = what + " " + opKO + " " + strjs(val)  # test name KO

            results.append(Test(test, nameOK, nameKO, strjs(tvalue)))

        list.__init__(self, results)

    def __repr__(self) -> str:
        return "".join(["[%s]" % repr(t) for t in self])


class Result:
    total = 0
    ok = 0
    infos = []

    @property
    def html(self):
        return render(self)

    @property
    def code(self):
        return self.total - self.ok


class ReqmanResult(Result):
    @classmethod
    def fromRMR(cls, name):
        if not name.endswith(".rmr"):
            name = name + ".rmr"
        with open(name, "rb") as fid:
            buf = fid.read()
            assert buf[:4] == b"RMR2"  # TODO
            x = zlib.decompress(buf[4:])
            return pickle.loads(x)

    def __init__(self, ll: T.List[Reqs], switches: list, env={}):
        ok = 0
        total = 0
        nbReqs = 0
        for r in ll:
            for x in r.exchanges:
                nbReqs += 1
                total += len(x.tests)
                ok += sum([t for t in x.tests])

        self.infos = [
            dict(
                date=datetime.datetime.now(),
                switches=switches,
                title="%s/%s" % (ok, total),
            )
        ]

        self.env = env
        self.ok = ok
        self.total = total
        self.nbReqs = nbReqs
        self.results = ll
        self.title = "%s %s/%s" % (",".join(switches), ok, total)

    @property
    def switches(self):
        return self.infos[0]["switches"]  # TODO: not top (but needed for replaying)

    def saveRMR(self, name=None):
        if name is None:
            name = (
                "_".join(
                    [self.infos[0]["date"].strftime("%y%m%d_%H%M")]
                    + self.infos[0]["switches"]
                )
                + ".rmr"
            )
        with open(name, "wb") as fid:
            x = pickle.dumps(self)
            fid.write(b"RMR2" + zlib.compress(x))
        return name


class ReqmanDualResult(Result):
    def __init__(self, r1: ReqmanResult, r2: ReqmanResult):
        assert len(r1.results) == len(r2.results)  # TODO: better here

        d1 = {i.name: i.exchanges for i in r1.results}
        d2 = {i.name: i.exchanges for i in r2.results}

        class ReqsMix:
            name = None
            exchanges = []

        ll = []
        for i in r1.results:
            m = ReqsMix()
            m.name = i.name
            ex1 = d1.get(i.name, [])
            ex2 = d2.get(i.name, [])

            m.exchanges = izip(ex1, ex2)
            if m.exchanges:
                ll.append(m)

        self.infos = [r1.infos[0], r2.infos[0]]

        self.env = None
        self.ok = r1.ok + r2.ok
        self.total = r1.total + r2.total
        self.nbReqs = r1.nbReqs + r2.nbReqs
        self.results = ll
        self.title = "%s vs %s" % (r1.title, r2.title)

        # for i in ll:
        #     print("FILE:",i.name)
        #     for ex,v1,v2 in i.exchanges:
        #         print("  ",ex.method,ex.path)
        #         if v1: print("    v1:",v1.method,v1.url)
        #         if v2: print("    v2:",v2.method,v2.url)


class Reqman:
    def __init__(self, conf=None):  # TODO: ability to pass env directly
        self.env = Env(conf)
        self.ymls = []  # list of str (or reqs)
        self.outputConsole = OutputConsole.MINIMAL

    def clone(self):
        r = Reqman(clone(self.env))
        r.ymls = self.ymls
        r.outputConsole = self.outputConsole
        return r

    @property
    def switches(self):
        return list(self.env.switches)

    def add(self, y):
        self.ymls.append(y)

    def execute(self, switches=[], paralleliz=False, http=None) -> ReqmanResult:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.asyncExecute(switches, paralleliz, http))

    async def asyncExecute(
        self, switches: list = [], paralleliz=False, http=None
    ) -> ReqmanResult:
        scope = self.env.clone()

        for switch in switches:
            scope.mergeSwitch(switch)

        reqsBegin = scope.getBEGIN()
        reqsEnd = scope.getEND()

        lreqs = []
        for yml in self.ymls:
            if isinstance(yml, Reqs):
                reqs = yml
                reqs.env = scope
                lreqs.append(reqs)
            else:
                lreqs.append(
                    Reqs(yml, scope)
                )  # (no need to clone) scope is cloned at execution time!

        results = []

        if reqsBegin is not None:
            await reqsBegin.asyncReqsExecute(switches, http)
            results.append(reqsBegin)

        if paralleliz:
            ll = [
                reqs.asyncReqsExecute(switches, http, outputConsole=self.outputConsole)
                for reqs in lreqs
            ]

            sem = asyncio.Semaphore(10)  # ten concurrent coroutine max
            async with sem:
                await asyncio.gather(*ll)
            results += lreqs
        else:
            for reqs in lreqs:
                await reqs.asyncReqsExecute(
                    switches, http, outputConsole=self.outputConsole
                )
                results.append(reqs)

        if reqsEnd is not None:
            await reqsEnd.asyncReqsExecute(
                switches, http, outputConsole=self.outputConsole
            )
            results.append(reqsEnd)

        r = ReqmanResult(results, switches, self.env)
        # ============================= LIVE CONSOLE
        if self.outputConsole != OutputConsole.NO:
            callback = cg if r.ok == r.total else cr
            print(
                "RESULT:", callback("%s/%s" % (r.ok, r.total)), "(%sreq(s))" % r.nbReqs
            )
        # ============================= LIVE CONSOLE

        return r


async def testContent(content: str, env: dict = {}, http=None) -> ReqmanResult:
    """ test a yml 'content' against env (easy wrapper for main call )"""
    if not isinstance(env, Env):
        env = Env(env)
    reqs = Reqs(content, env=env)
    await reqs.asyncReqsExecute([], http=http, outputConsole=OutputConsole.NO)

    return ReqmanResult([reqs], [], env)


def findRCup(cp):
    rqc = None
    while os.path.basename(cp) != "":
        if os.path.isfile(os.path.join(cp, REQMAN_CONF)):
            rqc = os.path.join(cp, REQMAN_CONF)
            break
        else:
            cp = os.path.realpath(os.path.join(cp, os.pardir))

    if rqc:
        try:
            print(cw("Use '%s'" % os.path.relpath(rqc)))
        except:
            print(cw("Use '%s'" % rqc))
    return rqc


class ReqmanCommand:
    def __init__(self, *params):
        self._r = Reqman()

        def listFiles(path: str, filters=(".yml", ".rml")) -> T.Iterator[str]:
            for folder, subs, files in os.walk(path):
                if (folder in [".", ".."]) or (
                    not os.path.basename(folder).startswith((".", "_"))
                ):
                    for filename in files:
                        if filename.lower().endswith(
                            filters
                        ) and not filename.startswith((".", "_")):
                            yield os.path.join(folder, filename)

        # expand list with file pattern matching (win needed)
        params = list(
            itertools.chain.from_iterable([glob.glob(i) or [i] for i in params])
        )
        files = []

        penv = {}
        for p in params:
            if os.path.isdir(p):
                files += sorted(list(listFiles(p)), key=lambda x: x.lower())
            elif os.path.isfile(p):
                files.append(p)
            elif ":" in p:
                key, value = p.split(":", 1)
                penv[key] = value
            else:
                raise RMException("bad param: '%s'" % p)  # TODO: better here

        files = [os.path.abspath(i) for i in files]  # TODO: really needed ?

        files.sort()
        cp = os.path.dirname(os.path.commonprefix(files)) or "."

        rqc = findRCup(cp)
        if rqc:
            self._r.env = Env(FString(rqc),rqc)

        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ SELFCONF
        self.fileSwitches = []
        for i in files:
            try:
                for s in yaml.load(FString(i), Loader=yaml.FullLoader):
                    if "conf" in s:
                        self.fileSwitches.extend(list(Env(s["conf"]).switches))
            except:
                pass
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        for k, v in penv.items():  # add param's input env into env
            self._r.env[k] = guessValue(v)

        for i in files:
            self._r.add(FString(i))

    @property
    def nbFiles(self):
        return len(self._r.ymls)

    @property
    def switches(self):
        return self._r.switches + self.fileSwitches

    def execute(
        self,
        switches=[],
        paralleliz=False,
        outputConsole=OutputConsole.MINIMAL,
        fakeServer=None,
    ) -> ReqmanResult:
        self._r.outputConsole = outputConsole
        return self._r.execute(switches, paralleliz, http=fakeServer)

    async def asyncExecute(
        self,
        switches=[],
        paralleliz=False,
        outputConsole=OutputConsole.MINIMAL,
        fakeServer=None,
    ) -> ReqmanResult:
        self._r.outputConsole = outputConsole
        return await self._r.asyncExecute(switches, paralleliz, http=fakeServer)

    async def asyncExecuteDual(
        self,
        switches1=[],
        switches2=[],
        outputConsole=OutputConsole.MINIMAL,
        fakeServer=None,
    ) -> ReqmanDualResult:
        self._r.outputConsole = outputConsole

        r2 = self._r.clone()  # clone IMPORTANT !!!

        ll = [
            self._r.asyncExecute(switches1, http=fakeServer),
            r2.asyncExecute(switches2, http=fakeServer),
        ]
        return ReqmanDualResult(*await asyncio.gather(*ll))


class ReqmanRMR(ReqmanCommand):
    def __init__(self, rmr: ReqmanResult):
        self._r = Reqman()
        self._r.env = rmr.env
        self._r.ymls = [i for i in rmr.results if i.name not in ["BEGIN", "END"]]

    # override
    async def asyncExecuteDual(
        self,
        switches1=[],
        switches2=[],
        outputConsole=OutputConsole.MINIMAL,
        fakeServer=None,
    ) -> ReqmanDualResult:
        raise RMException("not implemented")


def prettify(txt: str, indentation: int = 4) -> str:
    if txt == None:
        return ""
    else:
        txt = str(txt)
    try:
        return repr(Xml(txt))
    except:
        try:
            return jdumps(json.loads(txt), indent=indentation, sort_keys=True)
        except:
            return txt


def render(rr: Result) -> str:
    class LIMIT:
        TESTVALUE = 128
        HEADERVALUE = 512
        DOC = 1024
        TITLE = 1024
        BODY = 8192

    def limit(txt: str, size=None) -> str:
        if size and txt and len(txt) > int(size):
            info = "...***TRUNCATED***..."
            size = size - len(info)
            return txt[: size // 2] + info + txt[-size // 2 :]
        else:
            return txt

    template = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>{{result.title}}</title>
<meta name="description" content="reqman {{version}}">
<style>
* { box-sizing: border-box;}
.click {cursor:pointer}
html,body {width:100%;height:100%;margin:0px;padding:0px}
h3,h4 {padding:0px;margin:0px}
h3 {color: blue;margin-top:22px;}
h4 {padding:4px;background:#eee}
h4:hover {background: linear-gradient(to right,#EEE,white) !important}
h4 i {color:#AAA;font-weight: normal;font-size:0.9em}
body {font-family: sans-serif;font-size:90%}
pre {padding:4px;border:1px solid #CCC;max-height:300px;margin:2px;width:95%;display:block;overflow:auto;background:white}
.OK {color:green}
.KO {color:red}
div.r {margin:4px;background: linear-gradient(#EEE,white);margin-left:10px}
div.hide > div.h {background:white}
div.hide > h4 {background:white}
div.h {display:flex; flex-flow: row nowrap;padding-left:10px}
div.h > div {flex: 1 0 50%}
.nonp * {color:#888 !important;text-decoration: line-through;}
.expanderContent   {
    padding: 0;
    max-height: 700px;
    opacity: 1;
    overflow-y: auto;
    transition: 0.3s ease all;
    padding:4px;
    font-size:0.9em;
}
.hide .expanderContent {
    max-height: 0;
    opacity: 0;
    padding:0px
}

.cc:before{
  content:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAARCAYAAADUryzEAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5AMVCjI2TjtqdwAAAKlJREFUOMvd1LEJAjEYxfHfSUC0EezcQRB7KxsXcABLwQlcwh0EwQGcwDEcwcLCVvG0SXVezlMLwQevSPj4f/keSaCPE+41/KSABVpYx3VK7RQgwxmzwn6qHvJojUJBJx71+sI3TMo6LSN5XzFKjgG26BYBzdhhrFo7jMpGEDPJ1FTDl/oTwFuhlQFWmH4KCDhE/yaDUHJNAzap5xtrhqncejjW+BcumMMD+Ycv+JwSPxAAAAAASUVORK5CYII=) ;
  position:relative;
  left:0px;
  top:5px;
 }

.blinking{
    animation:blinkingText .3s;
}
@keyframes blinkingText{
    0%{     opacity: 1 }
    60%{    opacity: 0 }
    100%{   opacity: 1 }
}

</style>
<script>
function copyToClipboard( obj ) {
    obj.classList.toggle("blinking")
    setTimeout( function() {obj.classList.toggle("blinking")}, 300)
    var str=obj.textContent;

    const el = document.createElement('textarea');
    el.value = str;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
};
</script>
</head>
<body>
<div class="h" style="position:sticky">
%for i in result.infos:
    <div>
        <span style="float:right;padding:4px"><b>{{", ".join(i["switches"])}}</b> {{i["date"].strftime("%Y-%m-%d %H:%M:%S")}}<br/>
            <span style="float:right">{{i["title"]}}</span>
        </span>
    </div>
%end
</div>

%for r in result.results:
%if r:
<div class="f">
    <h3>File: {{relpath(r.name)}}</h3>

    %for ex in r.exchanges:
        % isLimit=not first(ex).nolimit
    <div class="r hide">
        <h4 class="click" onclick="this.parentElement.classList.toggle('hide')" title="Click to show/hide details">
            <b>{{first(ex).method}}</b>
            {{first_path(ex)}} <b style="float:right">{{first(ex).content if first(ex).status is None else first(ex).status}}</b>
            <br/>
            <i>{{limit(first(ex).doc,isLimit and LIMIT.DOC)}}</i>

        </h4>

<div class="h s expanderContent"><a class="cc click" onclick="copyToClipboard( this.parentNode )" title="copy"></a>
%for x in discover(ex):
    <div style="width:50%">
    %if x is not None:
<pre>
{{x.method}} {{x.url}}
%for k,v in x.inHeaders.items():
<b>{{k}}</b>: {{limit(v,isLimit and LIMIT.HEADERVALUE)}}
%end
{{limit(prettify(x.bodyContent),isLimit and LIMIT.BODY)}}</pre>
--> {{x.info}}

<pre>
%for k,v in genKV(x.outHeaders):
<b>{{k}}</b>: {{limit(v,isLimit and LIMIT.HEADERVALUE)}}
%end
{{limit(prettify(x.content),isLimit and LIMIT.BODY)}}</pre>
    %else:
        -
    %end
    </div>
%end
</div>



<div class="h">
%for x in discover(ex):
    <div style="width:50%" class="{{x and x.status==None and 'nonp'}}">
    %if x is not None:
        %for i in x.tests:
            <li class="{{i and "OK" or "KO"}}" title="{{limit(i.value,isLimit and LIMIT.TITLE)}}">{{i and "OK" or "KO"}} : {{limit(i.name,isLimit and LIMIT.TESTVALUE)}}</li>
        %end
    %else:
        -
    %end
    </div>
%end
</div>

    </div>
    %end


</div>
%end
%end
</body>
</html>
"""

    def discover(ex):
        if type(ex) is tuple:
            return list(ex)
        else:
            return [ex]

    def first(ex):
        if type(ex) is tuple:
            return ex[0] or ex[1]
        else:
            return ex

    def first_path(ex):
        if type(ex) is tuple:
            return first(ex).path
        else:
            return ex.url

    def relpath(p):
        try:
            return os.path.relpath(p, os.getcwd())
        except:
            return p

    return stpl.template(
        template,
        result=rr,
        prettify=prettify,
        discover=discover,
        first=first,
        relpath=relpath,
        first_path=first_path,
        version=__version__,
        limit=limit,
        LIMIT=LIMIT,
        genKV=genKV,
    )


def mkUrl(protocol: str, host: str, port=None) -> str:
    port = ":%s" % port if port else ""
    return "{protocol}://{host}{port}".format(**locals())


def create(url: str) -> T.Tuple[T.Union[None, str], str]:
    """ return a (reqman.conf, yml_file) based on the test 'url' """
    hp = urllib.parse.urlparse(url)
    if hp and hp.scheme and hp.hostname:
        root = mkUrl(hp.scheme, hp.hostname, hp.port)
        rc = (
            """
root: %(root)s
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
"""
            % locals()
        )

    else:
        root = ""
        rc = None

    path = hp.path + ("?" + hp.query if hp.query else "")

    yml = (
        u"""# test created for "%(root)s%(path)s" !

- GET: %(path)s
#- GET: %(root)s%(path)s
  tests:
    - status: 200
"""
        % locals()
    )
    return (rc, yml)


def extractParams(params):
    files, rparams, switches, dswitches = [], [], [], []
    for param in params:
        if param.startswith("--"):
            # reqman param
            p = param[2:]
            if p.startswith("o"):
                rparams.append(p)
            else:  # ability to group param (ex: --kspb)
                for i in p:
                    rparams.append(i)
        elif param.startswith("-"):
            # switch param
            switches.append(param[1:])
        elif param.startswith("+"):
            # dual switch param
            dswitches.append(param[1:])
        else:
            files.append(param)
    return files, rparams, switches, dswitches


def main(fakeServer=None, hookResults=None) -> int:
    params = sys.argv[1:]
    r = None

    class RMCommandException(Exception):
        pass

    # extract sys.argv in --> files,rparams,switch
    files, rparams, switches, dswitches = extractParams(params)

    isNewSheBang = (
        len(files) == 1
        and rparams == ["i"]
        and switches == []
        and dswitches == []
        and not files[0].endswith(".rmr")
    )
    if isNewSheBang:
        f = files[0]
        if os.path.isfile(f):
            with open(f, "r") as fid:
                firstLine = fid.readline()
            if firstLine.startswith("#!"):
                firstLine = firstLine.strip()
                print(cr("Use SHEBANG : %s") % firstLine)
                pp = firstLine.split(" ")[1:]
                exfiles, rparams, switches, dswitches = extractParams(pp)
                files.extend(exfiles)

    rmrFile = files[0] if len(files) == 1 and files[0].endswith(".rmr") else None

    # start the process
    try:
        if len(params) == 2 and params[0].lower() == "new":
            ## CREATE USAGE
            rc = findRCup(".")

            conf, yml = create(params[1])
            if conf:
                if not rc:
                    print("Create", REQMAN_CONF)
                    with open(REQMAN_CONF, "w") as fid:
                        fid.write(conf)
            else:
                if not rc:
                    raise RMException(
                        "there is no '%s', you shoul provide a full url !" % REQMAN_CONF
                    )

            ff = glob.glob("*_test.rml")
            yname = "%04d_test.rml" % ((len(ff) + 1) * 10)

            print("Create", yname)
            with open(yname, "w") as fid:
                fid.write(yml)

            return 0

        # control options
        paralleliz = False
        outputConsole = OutputConsole.MINIMAL
        outputHtmlFile = "reqman.html"
        openBrowser = False
        saveRMR = False
        replayRMR = False
        for p in rparams:
            if p == "k":
                outputConsole = OutputConsole.MINIMAL_ONLYKO
            elif p == "i":
                pass  # already managed (see below ^)
            elif p == "s":
                saveRMR = True
            elif p == "S":
                saveRMR = 2
            elif p == "r":  # TODO: write tests for thoses 3 conditions
                if switches:
                    raise RMCommandException("Can't set replay mode with switches")
                if dswitches:
                    raise RMCommandException("Can't set replay mode with switches")
                if not rmrFile:
                    raise RMCommandException(
                        "Can't set replay mode, you'll need a rmr file"
                    )
                replayRMR = True
            elif p == "p":
                paralleliz = True
                outputConsole = OutputConsole.MINIMAL_ONLYKO
            elif p.startswith("o"):
                outputHtmlFile = p[1:].strip(":= ")
                if not outputHtmlFile:
                    outputConsole = OutputConsole.FULL
            elif p.startswith("b"):
                openBrowser = True
            else:
                raise RMCommandException("bad option '%s'" % p)

        loop = asyncio.get_event_loop()
        if dswitches:
            # dual mode -> ReqmanDualResult
            if rmrFile:
                r = ReqmanRMR(ReqmanResult.fromRMR(rmrFile))

                rr1 = ReqmanResult.fromRMR(rmrFile)
                rr2 = loop.run_until_complete(
                    r.asyncExecute(
                        dswitches,
                        paralleliz=paralleliz,
                        outputConsole=outputConsole,
                        fakeServer=fakeServer,
                    )
                )
                rr = ReqmanDualResult(rr1, rr2)
            else:
                r = ReqmanCommand(*files)
                if saveRMR:
                    raise RMCommandException("Can't save dual results ;-)")

                if not all([s in [i[0] for i in r.switches] for s in switches]):
                    raise RMCommandException("bad switch")
                if not all([s in [i[0] for i in r.switches] for s in dswitches]):
                    raise RMCommandException("bad switch")
                if r.nbFiles < 1:
                    raise RMCommandException("no yml files found")

                rr = loop.run_until_complete(
                    r.asyncExecuteDual(
                        switches,
                        dswitches,
                        outputConsole=outputConsole,
                        fakeServer=fakeServer,
                    )
                )
        else:
            # single mode -> ReqmanResult or ReqmanDualResult
            if rmrFile:
                rmr = ReqmanResult.fromRMR(rmrFile)
                if not switches:
                    if replayRMR:  # -> ReqmanDualResult
                        r = ReqmanRMR(rmr)

                        rr1 = ReqmanResult.fromRMR(
                            rmrFile
                        )  # vv redeclare used switches (important ! fix 2.0.1)
                        rr2 = loop.run_until_complete(
                            r.asyncExecute(
                                rmr.switches,
                                paralleliz=paralleliz,
                                outputConsole=outputConsole,
                                fakeServer=fakeServer,
                            )
                        )
                        rr = ReqmanDualResult(rr1, rr2)
                    else:
                        rr = rmr
                else:
                    r = ReqmanRMR(rmr)
                    rr = loop.run_until_complete(
                        r.asyncExecute(
                            switches,
                            paralleliz=paralleliz,
                            outputConsole=outputConsole,
                            fakeServer=fakeServer,
                        )
                    )
            else:
                r = ReqmanCommand(*files)
                if not all([s in [i[0] for i in r.switches] for s in switches]):
                    raise RMCommandException("bad switch")
                if r.nbFiles < 1:
                    raise RMCommandException("no yml files found")

                rr = loop.run_until_complete(
                    r.asyncExecute(
                        switches,
                        paralleliz=paralleliz,
                        outputConsole=outputConsole,
                        fakeServer=fakeServer,
                    )
                )

        if saveRMR:
            if isinstance(rr, ReqmanResult):
                print("Save RMR:", rr.saveRMR("reqman.rmr" if saveRMR == 2 else None))

        if outputHtmlFile:
            with codecs.open(outputHtmlFile, "w+", "utf-8-sig") as fid:
                fid.write(rr.html)
            if openBrowser:
                try:
                    import webbrowser

                    webbrowser.open_new_tab(outputHtmlFile)
                except:
                    pass

        if hookResults is not None:  # for tests only
            hookResults.rr = rr

        return rr.code

    except KeyboardInterrupt:
        print("\nERROR: process interrupted")
        # loop.run_until_complete(close())
        return -1
    except RMFormatException as e:
        print("\nERROR FORMAT: %s" % e)
        return -1
    except RMException as e:
        print("\nERROR EXECUTION: %s" % e)
        return -1
    except RMCommandException as e:
        print("\nERROR COMMAND: %s" % e)

        print(
            """USAGE TEST   : reqman [--option] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version %s
Test a http service with pre-made scenarios, whose are simple yaml files
(More info on https://github.com/manatlan/reqman)

<folder|file> : yml scenario or folder of yml scenario
                (as many as you want)

[option]
        --k        : Limit standard output to failed tests (ko only)
        --p        : Paralleliz file tests (display only ko tests)
        --o:name   : Set a name for the html output file
        --o        : No html output file, but full console
        --b        : Open html output in browser if generated
        --s        : Save RMR file
        --r        : Replay the given RMR file in dual mode
        --i        : Use SHEBANG params (for a single file), alone
    """
            % __version__
        )
        if r and r.switches:
            print("[switch]")
            for k, v in r.switches:
                print("""%12s : "%s" """ % ("-" + k, v))
        else:
            print("""[switch]     : pre-made 'switch' defined in a %s""" % REQMAN_CONF)
        return -1
    except Exception as e:
        print(
            "\n**HERE IS A BUG**, please report it : https://github.com/manatlan/reqman/issues ;-)"
        )
        print(traceback.format_exc(), "\nBUG: %s" % e)
        return -1


if __name__ == "__main__":
    sys.exit(main())
