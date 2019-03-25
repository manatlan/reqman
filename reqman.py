#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# #############################################################################
#    Copyright (C) 2018-2019 manatlan manatlan[at]gmail(dot)com
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

__version__ = "1.1.2.3"

import yaml  # see "pip install pyyaml"
import encodings
import os
import json
import copy
import string
import sys
import ssl
import glob
import itertools
import html
import socket
import re
import copy
import collections
import io
import datetime
import email
import xml.dom.minidom
import http.cookies
import http.cookiejar
import http.client
import urllib.request
import urllib.parse
import urllib.error
import traceback


class NotFound:
    pass


class RMException(Exception): pass
class RMNonPlayable(Exception): pass


REQMAN_CONF = "reqman.conf"
KNOWNVERBS = set(
    ["GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS", "TRACE", "PATCH", "CONNECT"]
)

###########################################################################
## Utilities
###########################################################################
try:  # colorama is optionnal
    from colorama import init, Fore, Style

    init()

    cy = (
        lambda t: Fore.YELLOW + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL
        if t
        else None
    )
    cr = (
        lambda t: Fore.RED + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL
        if t
        else None
    )
    cg = (
        lambda t: Fore.GREEN + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL
        if t
        else None
    )
    cb = (
        lambda t: Fore.CYAN + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL
        if t
        else None
    )
    cw = (
        lambda t: Fore.WHITE + Style.BRIGHT + t + Fore.RESET + Style.RESET_ALL
        if t
        else None
    )
except ImportError:
    cy = cr = cg = cb = cw = lambda t: t

def chardet(s):
    """guess encoding of the string 's' -> cp1252 or utf8"""
    u8="çàâäéèêëîïôûù"
    cp=u8.encode("utf8").decode("cp1252")

    cu8,ccp=0,0
    for c in u8: cu8+=s.count(c)
    for c in cp: ccp+=s.count(c)

    if cu8>=ccp:
        return "utf8"
    else:
        return "cp1252"


def yamlLoad(fd):  # fd is an io thing
    b = fd.read()
    if type(b) == bytes:
        try:
            b = str(b, "utf8")
        except UnicodeDecodeError:
            b = str(b, "cp1252")
    else:
        encoding=chardet(b)
        b=b.encode(encoding).decode("utf8")
    return yaml.load(b)


def dict_merge(dct, merge_dct):
    """ merge 'merge_dct' in --> dct """
    for k, v in merge_dct.items():
        if (
            k in dct
            and isinstance(dct[k], dict)
            and isinstance(merge_dct[k], collections.abc.Mapping)
        ):
            dict_merge(dct[k], merge_dct[k])
        else:
            if k in dct and isinstance(dct[k], list) and isinstance(merge_dct[k], list):
                dct[k] += merge_dct[k]
            else:
                dct[k] = merge_dct[k]


def mkUrl(protocol, host, port=None):
    port = ":%s" % port if port else ""
    return "{protocol}://{host}{port}".format(**locals())


def prettify(txt, indentation=4):
    try:
        x = xml.dom.minidom.parseString(txt).toprettyxml(indent=" " * indentation)
        x = "\n".join(
            [s for s in x.splitlines() if s.strip()]
        )  # http://ronrothman.com/public/leftbraned/xml-dom-minidom-toprettyxml-and-silly-whitespace/
        return x
    except:
        try:
            return json.dumps(json.loads(txt), indent=indentation, sort_keys=True)
        except:
            return txt


def jpath(elem, path):
    for i in path.strip(".").split("."):
        try:
            if type(elem) == list:
                if i == "size":
                    return len(elem)
                else:
                    elem = elem[int(i)]
            elif type(elem) == dict:
                if i == "size":
                    return len(list(elem.keys()))
                else:
                    elem = elem.get(i, NotFound)
            elif type(elem) == str:
                if i == "size":
                    return len(elem)
        except (ValueError, IndexError) as e:
            return NotFound
    return elem


###########################################################################
## http request/response
###########################################################################
class CookieStore(http.cookiejar.CookieJar):
    """ Manage cookiejar for httplib-like """

    def saveCookie(self, headers, url):
        if type(headers) == dict:
            headers = list(headers.items())

        class FakeResponse:
            def __init__(self, headers=[], url=None):
                """
                headers: list of RFC822-style 'Key: value' strings
                """
                m = email.message_from_string("\n".join(headers))
                self._headers = m
                self._url = url

            def info(self):
                return self._headers

        response = FakeResponse([": ".join([k, v]) for k, v in headers], url)
        self.extract_cookies(response, urllib.request.Request(url))

    def getCookieHeaderForUrl(self, url):
        r = urllib.request.Request(url)
        self.add_cookie_header(r)
        return dict(r.header_items())


COOKIEJAR = CookieStore()


class Request:
    def __init__(self, protocol, host, port, method, path, body=None, headers={}):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.method = method
        self.path = path
        self.body = body
        self.headers = {}

        if self.protocol:
            self.url = mkUrl(self.protocol, self.host, self.port) + self.path
            self.headers = COOKIEJAR.getCookieHeaderForUrl(self.url)
        else:
            self.url = None

        self.headers.update(headers)

    def __repr__(self):
        return cy(self.method) + " " + self.path


class Content:
    def __init__(self, content):
        self.__b = content if type(content) == bytes else bytes(content, "utf8")

    def toBinary(self):
        return self.__b

    def __repr__(self):
        try:
            return str(self.__b, "utf8")  # try as utf8 ...
        except UnicodeDecodeError:
            try:
                return str(self.__b, "cp1252")  # try as cp1252 ...
            except UnicodeDecodeError:
                # fallback to a *** binary representation ***
                return "*** BINARY SIZE(%s) ***" % len(self.__b)

    def __contains__(self, key):
        return key in str(self)


class Response:
    def __init__(self, status, body, headers, url, info=None):
        self.status = int(status)
        self.content = Content(body)
        self.headers = dict(headers)  # /!\ cast list of 2-tuple to dict ;-(
        # eg: if multiple "set-cookie" -> only the last is kept
        self.info = info
        COOKIEJAR.saveCookie(headers, url)

    def __repr__(self):
        return str(self.status)


class ResponseError:
    def __init__(self, m):
        self.status = None
        self.content = m
        self.headers = {}
        self.info = ""
        self.time=None

    def __repr__(self):
        return "ERROR: %s" % (self.content)


def dohttp(r):
    try:
        if r.protocol and r.protocol.lower() == "https":
            cnx = http.client.HTTPSConnection(
                r.host, r.port, context=ssl._create_unverified_context()
            )  # TODO: ability to setup a verified ssl context ?
        else:
            cnx = http.client.HTTPConnection(r.host, r.port)
        enc = lambda x: x.replace(" ", "%20")
        cnx.request(r.method, enc(r.path), r.body, r.headers)
        rr = cnx.getresponse()

        info = "%s %s %s" % (
            {10: "HTTP/1.0", 11: "HTTP/1.1"}.get(rr.version, "HTTP/?"),
            rr.status,
            rr.reason,
        )

        return Response(rr.status, rr.read(), rr.getheaders(), r.url, info)
    except socket.timeout:
        return ResponseError("Response timeout")
    except socket.error:
        return ResponseError("Server is down ?!")
    except http.client.BadStatusLine:
        # A subclass of HTTPException. Raised if a server responds with a HTTP status code that we don’t understand.
        # Presumably, the server closed the connection before sending a valid response.
        return ResponseError("Server closed the connection")


###########################################################################
## Reqs manage
###########################################################################
class Test(int):
    """ a boolean with a name """

    def __new__(cls, value, nameOK, nameKO):
        s = super(Test, cls).__new__(cls, value)
        if value:
            s.name = nameOK
        else:
            s.name = nameKO
        return s


def getValOpe(v):
    try:
        if type(v) == str and v.startswith("."):
            g = re.match(r"^\. *([!=<>]{1,2}) *(.+)$", v)
            if g:
                op, v = g.groups()
                vv = yaml.load(v)
                if op == "==":  # not needed really, but just for compatibility
                    return vv, lambda a, b: b == a, "=", "!="
                elif op == "=":  # not needed really, but just for compatibility
                    return vv, lambda a, b: b == a, "=", "!="
                elif op == "!=":
                    return vv, lambda a, b: b != a, "!=", "="
                elif op == ">=":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b >= a or False,
                        ">=",
                        "<",
                    )
                elif op == "<=":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b <= a or False,
                        "<=",
                        ">",
                    )
                elif op == ">":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b > a or False,
                        ">",
                        "<=",
                    )
                elif op == "<":
                    return (
                        vv,
                        lambda a, b: b != None and a != None and b < a or False,
                        "<",
                        ">=",
                    )
    except (
        yaml.scanner.ScannerError,
        yaml.constructor.ConstructorError,
        yaml.parser.ParserError,
    ):
        pass
    return v, lambda a, b: a == b, "=", "!="


def strjs(x):
    return json.dumps(x,ensure_ascii=False)


class TestResult(list):
    def __init__(self, req, res, tests, doc=None):
        self.req = req
        self.res = res
        self.doc = doc

        insensitiveHeaders = (
            {k.lower(): v for k, v in self.res.headers.items()} if self.res else {}
        )

        results = []
        for test in tests:
            what, value = list(test.keys())[0], list(test.values())[0]

            testContains = False

            # get the value to compare with value --> tvalue
            if what == "content":
                testContains = True
                tvalue = str(self.res.content)
            elif what == "status":
                testContains = False
                tvalue = self.res.status
            elif what.startswith("json."):
                testContains = False
                try:
                    jzon = json.loads(str(self.res.content))
                    tvalue = jpath(jzon, what[5:])
                    tvalue = None if tvalue == NotFound else tvalue
                except Exception as e:
                    tvalue = None
            else:  # headers
                testContains = True
                tvalue = insensitiveHeaders.get(what.lower(), "")

            # test if all match as json (list, dict, str ...)
            try:
                j = lambda x: json.dumps(
                    json.loads(x) if type(x) in [str, bytes] else x, sort_keys=True
                )
                matchAll = j(value) == j(tvalue)
            except json.decoder.JSONDecodeError as e:
                matchAll = False

            if matchAll:
                test, opOK, opKO, val = True, "=", "!=", value
            else:
                # ensure that we've got a list
                values = [value] if type(value) != list else value

                bool = False
                for value in values:  # match any
                    if testContains:
                        value, ope, opOK, opKO = (
                            value,
                            lambda x, c: x in c,
                            "contains",
                            "doesn't contain",
                        )
                    else:
                        value, ope, opOK, opKO = getValOpe(value)

                    bool = ope(value, tvalue)
                    if bool:
                        break

                if len(values) == 1:
                    test, opOK, opKO, val = bool, opOK, opKO, value
                else:
                    test, opOK, opKO, val = (
                        bool,
                        "matchs any",
                        "doesn't match any",
                        values,
                    )

            results.append(
                Test(
                    test,
                    what + " " + opOK + " " + strjs(val),  # test name OK
                    what + " " + opKO + " " + strjs(val),  # test name KO
                )
            )

        list.__init__(self, results)

    def __repr__(self):
        ll = [""]
        ll.append(
            cy("*")
            + " %s --> %s"
            % (self.req, cw(str(self.res)) if self.res else cr("Not callable"))
        )
        for t in self:
            ll.append("  - %s: %s" % (cg("OK") if t == 1 else cr("KO"), t.name))
        return "\n".join(ll)


def getVar(env, var):
    if var in env:
        return txtReplace(env, env[var])
    elif "|" in var:
        key, method = var.split("|", 1)

        content = env.get(key, key)  # resolv keys else use it a value !!!!!
        content = txtReplace(env, content)
        for m in method.split("|"):
            content = transform(content, env, m)
            content = txtReplace(env, content)
        return content

    elif "." in var:
        val = jpath(env, var)
        if val is NotFound:
            raise RMNonPlayable(
                "Can't resolve " + var + " in : " + ", ".join(list(env.keys()))
            )
        return txtReplace(env, val)
    else:
        raise RMNonPlayable(
            "Can't resolve " + var + " in : " + ", ".join(list(env.keys()))
        )


def transform(content, env, methodName):
    if methodName:
        if methodName in env:
            code = getVar(env, methodName)
            try:
                exec(
                    "def DYNAMIC(x,ENV):\n"
                    + ("\n".join(["  " + i for i in code.splitlines()])),
                    globals(),
                )
            except Exception as e:
                raise RMException(
                    "Error in declaration of method " + methodName + " : " + str(e)
                )
            try:
                x = json.loads(content)
            except (json.decoder.JSONDecodeError, TypeError):
                x = content
            try:
                if transform.path:
                    curdir = os.getcwd()
                    os.chdir(transform.path)
                content = DYNAMIC(x, env)
            except Exception as e:
                raise RMException(
                    "Error in execution of method " + methodName + " : " + str(e)
                )
            finally:
                if transform.path:
                    os.chdir(curdir)
        else:
            raise RMException(
                "Can't find method "
                + methodName
                + " in : "
                + ", ".join(list(env.keys()))
            )

    return content


transform.path = None  # change cd cwd for transform methods when executed


def objReplace(env, txt):  # same as txtReplace() but for "object" (json'able)
    obj = txtReplace(env, txt)
    try:
        obj = json.loads(obj)
    except (json.decoder.JSONDecodeError, TypeError):
        pass
    return obj


def txtReplace(env, txt):
    if env and txt and isinstance(txt, str):
        for vvar in re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt):
            var = vvar[2:-2]

            try:
                val = getVar(
                    env, var
                )  # recursive here ! (if myvar="{{otherVar}}"", redo a pass to resolve otherVar)
            except RuntimeError:
                raise RMException("Recursion trouble for '%s'" % var)

            if val is NotFound:
                raise RMNonPlayable(
                    "Can't resolve " + var + " in : " + ", ".join(list(env.keys()))
                )
            else:
                if type(val) != str:
                    if val is None:
                        val = ""  # TODO: should be "null" !!!!
                    elif val is True:
                        val = "true"
                    elif val is False:
                        val = "false"
                    elif type(val) in [list, dict]:
                        val = json.dumps(val)
                    elif type(val) == bytes:
                        val = str(val, "utf8")  # TODO: good ? NEED MORE TESTS !!!!!
                    else:  # int, float, ...
                        val = json.dumps(val)

                # ~ txt=txt.replace( vvar , str(val, "utf-8") if type(val)!=str else val )
                txt = txt.replace(vvar, val)

    return txt


def warn(*m):
    print("***WARNING***", *m)


def getTests(y):
    """ Get defined tests as list ok dict key:value """
    if y:
        tests = y.get("tests", [])
        if type(tests) == dict:
            warn(
                "'tests:' should be a list of mono key/value pairs (ex: '- status: 200')"
            )
            tests = [{k: v} for k, v in tests.items()]
        return tests
    else:
        return []


def getHeaders(y):
    """ Get defined headers as dict """
    if y:
        headers = y.get("headers", {})
        if type(headers) == list:
            warn(
                "'headers:' should be filled of key/value pairs (ex: 'Content-Type: text/plain')"
            )
            headers = {list(d.keys())[0]: list(d.values())[0] for d in headers}
        return headers
    else:
        return {}


class Req(object):
    def __init__(
        self,
        method,
        path,
        body=None,
        headers={},
        tests=[],
        saves=[],
        params={},
        doc=None,
    ):  # body = str ou dict ou None
        self.method = method.upper()
        self.path = path
        self.body = body
        self.headers = headers
        self.tests = tests
        self.saves = saves
        self.params = params
        self.doc = doc

    def clone(self):
        return Req(
            self.method,
            self.path,
            copy.deepcopy(self.body),
            dict(self.headers),
            list(self.tests),
            list(self.saves),
            dict(self.params),
            self.doc,
        )

    def test(self, env=None):
        cenv = env.copy() if env else {}  # current env
        cenv.update(self.params)  # override with self params

        err=None # to handle NonPlayable test (not a error anymore, a TestResult is returned)

        # path ...
        try:
            path = txtReplace(cenv, self.path)
        except RMNonPlayable as e:
            path=self.path
            err=e
        
        if cenv and (not path.strip().lower().startswith("http")) and ("root" in cenv):
            h = urllib.parse.urlparse(cenv["root"])
            if h.path and h.path[-1] == "/":
                if path[0] == "/":
                    path = h.path + path[1:]
                else:
                    path = h.path + path
            else:
                path = h.path + path
        else:
            h = urllib.parse.urlparse(path)
            path = h.path + ("?" + h.query if h.query else "")

        # headers ...
        headers = getHeaders(cenv).copy() if cenv else {}
        headers.update(self.headers)  # override with self headers
        headers = {
            k: txtReplace(cenv, v) for k, v in list(headers.items()) if v is not None
        }

        # fill tests ...
        tests = getTests(cenv)
        tests += self.tests  # extends with self tests

        ntests = []
        for test in tests:
            key, val = list(test.keys())[0], list(test.values())[0]
            if type(val) == list:
                val = [txtReplace(cenv, i) for i in val]
            else:
                val = txtReplace(cenv, val)
            ntests.append({key: val})
        tests = ntests

        # body ...
        if self.body and not isinstance(self.body, str):
            jrep = lambda x: objReplace(cenv, x)  # "json rep"

            # ================================
            def apply(body, method):
                if type(body) == list:
                    return [apply(i, method) for i in body]
                elif type(body) == dict:
                    return {k: apply(v, method) for k, v in body.items()}
                else:
                    return method(body)

            # ================================

            body = apply(self.body, jrep)
            body = json.dumps(body)  # and convert to string !
        else:
            try:
                body = txtReplace(cenv, self.body)
                body = txtReplace(cenv, body)   #TODO: make something's better (to avoid this multiple call) ... here it's horrible, but needed for test_param/test_param_resolve
            except RMNonPlayable as e:
                # return a TestResult Error ....
                body=self.body

        if err:
            req = Request(h.scheme, h.hostname, h.port, self.method, path, body, headers)
            res=ResponseError( str(err) )
            return TestResult(req, res,  tests, self.doc)
        else:
            req = Request(h.scheme, h.hostname, h.port, self.method, path, body, headers)
            if h.hostname:

                timeout = cenv.get("timeout", None)
                try:
                    socket.setdefaulttimeout(timeout and float(timeout) / 1000.0)
                except ValueError:
                    socket.setdefaulttimeout(None)

                t1 = datetime.datetime.now()
                res = dohttp(req)
                res.time = datetime.datetime.now() - t1
                if isinstance(res, Response) and self.saves:
                    for save in self.saves:
                        dest = txtReplace(cenv, save)
                        if dest.lower().startswith("file://"):
                            name = dest[7:]
                            try:
                                with open(name, "wb+") as fid:
                                    fid.write(res.content.toBinary())
                            except Exception as e:
                                raise RMException(
                                    "Save to file '%s' error : %s" % (name, e)
                                )
                        else:
                            if dest:
                                try:
                                    env[dest] = json.loads(str(res.content))
                                    cenv[dest] = json.loads(str(res.content))
                                except json.decoder.JSONDecodeError:
                                    env[dest] = str(res.content)
                                    cenv[dest] = str(res.content)

                return TestResult(req, res, tests, self.doc)
            else:
                # no hostname : no response, no tests ! (missing reqman.conf the root var ?)
                return TestResult(req, None, [], self.doc)

    def __repr__(self):
        return "<%s %s>" % (self.method, self.path)


def controle(keys, knowkeys):
    for key in keys:
        if key not in knowkeys:
            raise RMException("Not a valid entry '%s'" % key)


class Reqs(list):
    def __init__(self, fd, env=None):
        self.env = env or {}  # just for proc finding
        self.name = fd.name.replace("\\", "/") if hasattr(fd, "name") else "String"
        self.trs = []
        if not hasattr(fd, "name"):
            setattr(fd, "name", "<string>")
        try:
            l = yamlLoad(fd)
        except Exception as e:
            raise RMException("YML syntax in %s\n%s" % (fd.name or "<string>", e))

        procs = {}

        def feed(l):
            l = l if type(l) == list else [l]

            ll = []
            for entry in l:
                if not entry:
                    continue
                env = {}
                dict_merge(env, self.env)

                try:
                    if type(entry) != dict:
                        if type(entry)==str and entry=="break":
                            break
                        else:
                            raise RMException("no actions for %s" % entry)
                    action = list(
                        (KNOWNVERBS | set(["call"])).intersection(list(entry.keys()))
                    )
                    if len(action) > 1:
                        raise IndexError
                    else:
                        action = action[0]
                except IndexError:
                    action = None

                if action is not None:
                    # a real action (call a proc or a requests)
                    headers = getHeaders(entry)
                    tests = getTests(entry)
                    params = entry.get("params", {})
                    foreach = entry.get("foreach", [None])  # at least one iteration !
                    saves = entry.get("save", [])
                    saves = saves if type(saves) == list else [saves]

                    if type(params) == dict:
                        dict_merge(env, params)  # add current params (to find proc)
                    else:
                        raise RMException("params is not a dict : '%s'" % params)

                    if foreach and type(foreach) == str:
                        foreach = objReplace(env, foreach)

                    if action == "call":
                        controle(
                            entry.keys(),
                            ["headers", "tests", "params", "foreach", "save", "call"],
                        )

                        procnames = entry["call"]

                        if procnames and type(procnames) == str:
                            procnames = objReplace(env, procnames)

                        procnames = (
                            procnames if type(procnames) == list else [procnames]
                        )

                        for procname in procnames:
                            procname = objReplace(env, procname)
                            content = procs.get(procname, env.get(procname, None))
                            if content is None:
                                raise RMException(
                                    "unknown procedure '%s' is %s"
                                    % (procname, procs.keys())
                                )

                            for param in foreach:
                                if type(param) == str:
                                    param = objReplace(env, param)
                                for req in feed(content):
                                    newreq = req.clone()
                                    newreq.tests += tests  # merge tests
                                    dict_merge(newreq.headers, headers)  # merge headers
                                    dict_merge(newreq.params, params)  # merge params
                                    if param:
                                        dict_merge(
                                            newreq.params, param
                                        )  # merge foreach param
                                    newreq.saves += saves  # merge saves

                                    ll.append(newreq)
                    else:
                        controle(
                            entry.keys(),
                            [
                                "headers",
                                "doc",
                                "tests",
                                "params",
                                "foreach",
                                "save",
                                "body",
                            ]
                            + list(KNOWNVERBS),
                        )

                        body = entry.get("body", None)
                        doc=entry.get("doc", None)                                    

                        if foreach and type(foreach)!=list:
                            raise RMException("the foreach section is not a list ?!")

                        for param in foreach:
                            if type(param) == str:
                                param = objReplace(env, param)

                            lparams = {}
                            dict_merge(lparams, params)
                            if param:
                                dict_merge(lparams, param)
                            ll.append(
                                Req(
                                    action,
                                    entry[action],
                                    body,
                                    headers,
                                    tests,
                                    saves,
                                    lparams,
                                    doc,
                                )
                            )

                elif len(entry) == 1 and type(list(entry.values())[0]) in [list, dict]:
                    # a proc declared
                    procname, content = list(entry.items())[0]
                    if procname in [
                        "headers",
                        "tests",
                        "params",
                        "foreach",
                        "save",
                        "body",
                    ]:
                        raise RMException("procedure can't be named %s" % procname)
                    procs[procname] = content
                else:
                    # no sense ?!
                    raise RMException("no action or too many : %s" % entry.keys())

            return ll

        list.__init__(self, feed(l))


###########################################################################
## Helpers
###########################################################################
def listFiles(path, filters=(".yml", ".rml")):
    for folder, subs, files in os.walk(path):
        if folder in [".", ".."] or (
            not os.path.basename(folder).startswith((".", "_"))
        ):
            for filename in files:
                if filename.lower().endswith(filters):
                    yield os.path.join(folder, filename)


def loadEnv(fd, varenvs=[]):
    transform.path = None
    if fd:
        if not hasattr(fd, "name"):
            setattr(fd, "name", "")
        try:
            env = yamlLoad(fd) if fd else {}
            if fd.name:
                print(cw("Using '%s'" % os.path.relpath(fd.name)))
                transform.path = os.path.dirname(
                    fd.name
                )  # change path when executing transform methods, according the path of reqman.conf
        except Exception as e:
            raise RMException("YML syntax in %s\n%s" % (fd.name or "<string>", e))
    else:
        env = {}

    for name in varenvs:
        if name not in env:
            raise RMException("the switch '-%s' is unknown ?!" % name)
        else:
            dict_merge(env, env[name])
    return env


def render(reqs, switchs):
    h = """
<meta charset="utf-8">
<style>
body {font-family: sans-serif;font-size:90%}
.ok {color:green}
.ko {color:red}
hr {padding:0px;margin:0px;height: 1px;border: 0;color: #CCC;background-color: #CCC;}
pre {padding:4px;border:1px solid black;background:white !important;overflow-x:auto;width:100%;max-height:300px;margin:2px;}
span.title {cursor:pointer;}
span.title:hover {background:#EEE;}
i {float:right;color:#AAA}
i.bad {color:orange}
i.good {color:green}
ol,ul {margin:0px;}
ol {padding:0px;}
ol > li {background:#FFE;border-bottom:1px dotted grey;padding:4px;margin-left:16px}
li.hide {background:inherit}
li.hide > ul > span {display:none}
h3 {color:blue;margin:8 0 0 0;padding:0px}
.info {position:fixed;top:0px;right:0px;background:rgba(1,1,1,0.2);border-radius:4px;text-align:right;padding:4px}
.info > * {display:block}
</style>
"""
    alltr = []
    for f in reqs:
        times = [tr.res.time for tr in f.trs if tr.res and tr.res.time]

        reqs = ""
        for tr in f.trs:
            alltr += tr

            qheaders = "\n".join(
                ["<b>%s</b>: %s" % (k, v) for k, v in list(tr.req.headers.items())]
            )
            qbody = prettify(str(tr.req.body or ""))

            qdoc = "<b>%s</b>" % tr.doc if tr.doc else ""

            if tr.res and tr.res.status is not None:
                rtime = tr.res.time
                info = tr.res.info
                rheaders = "\n".join(
                    ["<b>%s</b>: %s" % (k, v) for k, v in list(tr.res.headers.items())]
                )
                rbody = prettify(str(tr.res.content or ""))

                hres = """
                    {qdoc}
                    <pre title="the request">{tr.req.method} {tr.req.url}<hr/>{qheaders}<hr/>{qbody}</pre>
                    -> {info}
                    <pre title="the response">{rheaders}<hr/>{rbody}</pre>
                """.format(
                    **locals()
                )

            else:
                rtime = ""

                hres = """
                    {qdoc}
                    <pre title="the request">{tr.req.method} {tr.req.url}<hr/>{qheaders}<hr/>{qbody}</pre>
                """.format(
                    **locals()
                )

            tests = "".join(
                [
                    """<li class='%s'>%s</li>"""
                    % ("ok" if t else "ko", t.name)
                    for t in tr
                ]
            )

            reqs += """
<li class="hide">
    <span class="title" onclick="this.parentElement.classList.toggle('hide')" title="Click to show/hide details"><b>{tr.req.method}</b> {tr.req.path} : <b>{tr.res}</b> <i>{rtime}</i></span>
    <ul>
        <span>
            {hres}
        </span>
        {tests}
    </ul>
</li>
            """.format(
                **locals()
            )

        avg = sum(times, datetime.timedelta()) / len(times) if len(times) else 0
        h += """<h3>%s</h3>
        <ol>
            <i style='float:inherit'>%s req(s) avg = %s</i>
            %s
        </ol>""" % (
            f.name,
            len(times),
            avg,
            reqs,
        )

    ok, total = len([i for i in alltr if i]), len(alltr)

    h += """<title>Result: %(ok)s/%(total)s</title>
    <div class='info'><span>%(today)s</span><b>%(switchs)s</b></div>""" % dict(
        ok=ok,
        total=total,
        today=str(datetime.datetime.now())[:16],
        switchs=" ".join(switchs),
    )

    with open("reqman.html", "w+", encoding="utf_8") as fid:
        fid.write(h)

    return ok, total


def findRCUp(fromHere):
    """Find the rc in upwards folders"""
    current = os.path.realpath(fromHere)
    while 1:
        rc = os.path.join(current, REQMAN_CONF)
        if os.path.isfile(rc):
            break
        next = os.path.realpath(os.path.join(current, ".."))
        if next == current:
            rc = None
            break
        else:
            current = next
    return rc


def resolver(params):
    """ return tuple (reqman.conf,ymls) finded with params """
    ymls, paths = [], []

    # expand list with file pattern matching (win needed)
    params = list(itertools.chain.from_iterable([glob.glob(i) or [i] for i in params]))

    for p in params:
        if os.path.isdir(p):
            ymls += sorted(list(listFiles(p)), key=lambda x: x.lower())
            paths += [os.path.dirname(i) for i in ymls]
        elif os.path.isfile(p):
            paths.append(os.path.dirname(p))
            ymls.append(p)
        else:
            raise RMException("bad param: %s" % p)  # TODO: better here

    # choose first reqman.conf under choosen files
    rc = None
    folders = list(set(paths))
    folders.sort(key=lambda i: i.count("/") + i.count("\\"))
    for f in folders:
        if os.path.isfile(os.path.join(f, REQMAN_CONF)):
            rc = os.path.join(f, REQMAN_CONF)

    # if not, take the first reqman.conf in backwards
    if rc is None:
        rc = findRCUp(folders[0] if folders else ".")

    ymls.sort(key=lambda x: x.lower())
    return rc, ymls


def makeReqs(reqs, env):
    if reqs:
        if env and ("BEGIN" in env):
            r = io.StringIO("call: BEGIN")
            r.name = "BEGIN (%s)" % REQMAN_CONF
            reqs = [Reqs(r, env)] + reqs

        if env and ("END" in env):
            r = io.StringIO("call: END")
            r.name = "END (%s)" % REQMAN_CONF
            reqs = reqs + [Reqs(r, env)]

    return reqs


def create(url):
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
    return rc, yml


def main(params=[]):
    reqs = []
    switchs = []
    try:
        if len(params) == 2 and params[0].lower() == "new":
            ## CREATE USAGE
            rc = findRCUp(".")
            if rc:
                print(cw("Using '%s'" % os.path.relpath(rc)))

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

        # search for a specific env var (starting with "-")
        switchs = []
        for switch in [i for i in params if i.startswith("-")]:
            params.remove(switch)
            switchs.append(switch[1:])

        if "-ko" in switchs:
            switchs.remove("-ko")
            onlyFailedTests = True
        else:
            onlyFailedTests = False

        rc, ymls = resolver(params)

        # load env !
        if rc:
            with open(rc, "r") as fid:
                env = loadEnv(fid, switchs)
        else:
            env = loadEnv(None, switchs)

        ll = []
        for i in ymls:
            with open(i, "r") as fid:
                ll.append(Reqs(fid, env))

        reqs = makeReqs(ll, env)

        if reqs:
            # and make tests
            for f in reqs:
                f.trs = []
                print("\nTESTS:", cb(f.name))
                for t in f:
                    tr = t.test(env)  # TODO: colorful output !
                    if onlyFailedTests:
                        if not all(tr):
                            print(tr)
                    else:
                        print(tr)
                    f.trs.append(tr)

            ok, total = render(reqs, switchs)

            if total:
                print("\nRESULT: ", (cg if ok == total else cr)("%s/%s" % (ok, total)))

            # expose things inproc, for tests purpose only
            main.total = total
            main.ok = ok
            main.env = env
            main.reqs = reqs
            return total - ok
        else:
            print(
                """USAGE TEST   : reqman [--option] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version %s
Test a http service with pre-made scenarios, whose are simple yaml files
(More info on https://github.com/manatlan/reqman)

  <folder|file> : yml scenario or folder of yml scenario
                  (as many as you want)

  [option]
           --ko : limit standard output to failed tests (ko) only
"""
                % __version__
            )

            if env:
                print("""  [switch]      : default to "%s" """ % env.get("root", None))
                for k, v in env.items():
                    root = v.get("root", None) if type(v) == dict else None
                    if root:
                        print("""%15s : "%s" """ % ("-" + k, root))
            else:
                print(
                    """  [switch]      : pre-made 'switch' defined in a %s"""
                    % REQMAN_CONF
                )
            return -1

    except RMException as e:
        print("\nERROR: %s" % e)
        return -1
    except Exception as e:
        print("\n**HERE IS A BUG**, please report it !")
        print(traceback.format_exc(), "\nERROR: %s" % e)
        return -1
    except KeyboardInterrupt as e:
        render(reqs, switchs)
        print("\nERROR: process interrupted")
        return -1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
    # exec(open("tests.py").read())
