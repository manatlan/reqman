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

import os, sys, re, asyncio, io, datetime, itertools, glob, enum, codecs
import urllib
import urllib.parse
import collections, json
import typing as T
import sys, traceback
import pickle, zlib
import encodings.idna

# import httpcore # see "pip install httpcore"
import yaml  # see "pip install pyyaml"
import stpl  # see "pip install stpl"
import xpath  # see "pip install py-dom-xpath-six"
import jwt  # (pip install pyjwt) just for pymethods in rml files (useful to build jwt token)

import newcore # NEW CORE SYSTEM


# 97% coverage: python3 -m pytest --cov-report html --cov=reqman .
__version__ = "3.0.0.0"  # only SemVer (the last ".0" is win only)

if getattr( sys, 'frozen', False ) : # when frozen/pyinstaller
    REQMANEXE = sys.executable
else :
    REQMANEXE = os.path.splitext(os.path.basename(sys.argv[0]))[0]

__usage__="""USAGE TEST   : %s [--option] [-switch] <folder|file>...
USAGE CREATE : %s new <url>
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
        --f        : Force full output in html rendering
        --x:var    : Special mode to output an env var (as json output)
""" % (REQMANEXE,REQMANEXE,__version__)

EXPOSEDS={}  #to be able to expose real python code as {"functName": <callable>, ...}

def expose(fn): #decorator to expose a real python method in resolver
    EXPOSEDS[fn.__name__]=fn
    return fn

try:  # colorama is optionnal
    from colorama import init, Fore, Style

    init()

    def colorize(color: int, t: str) -> T.Union[str, None]:
        return (color + Style.BRIGHT + str(t) + Fore.RESET + Style.RESET_ALL if t else None)

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
KNOWNACTIONEXT = ["headers", "doc", "tests", "params", "foreach", "save", "body", "if", "query"]
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




class Env(dict):
    path=None

    def __init__(self, d=None, path=None):
        self.path=path and os.path.dirname(path) or None
        if not d:
            d = {}

        if isinstance(d, str):
            d = ustr(d)
            try:
                d = yaml.load(d, Loader=yaml.SafeLoader)
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

    @property
    def globals(self):
        return self.__global

    def clone(self, cloneSharedScope=True):
        newOne = Env({})
        dict_merge(newOne, self)


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

    def replaceObj(self, o: T.Any) -> T.Any:  # same as txtReplace() but for "object" (json'able)
        """ DEPRECATED """

        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        d=dict(self.clone())
        return newcore.env.Scope(d,EXPOSEDS).resolve_all(o)
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

    def replaceTxt(self, txt: str) -> T.Union[str, bytes]:
        """ DEPRECATED """
        assert type(txt) is str

        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        d=dict(self.clone())
        try:
            return newcore.env.Scope(d,EXPOSEDS).resolve_string(txt)
        except newcore.env.ResolveException:
            return txt
        except newcore.env.PyMethodException as e:
            raise RMPyException(e)
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\


    def replaceObjOrNone(self, v: T.Any) -> T.Any:  # same as txtReplace() but for "object" (json'able)
        """ DEPRECATED """

        v = self.replaceObj(v)
        return v if self.getNonResolvedVars(v) == [] else None

    def getNonResolvedVars(self, txt):
        """ DEPRECATED """
        if type(txt) == str:
            return re.findall(r"\{\{[^\}]+\}\}", txt) + re.findall("<<[^><]+>>", txt)
        else:
            return []


    def __str__(self):
        return newcore.common.jdumps(self, indent=4, sort_keys=True)

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.__dict__ = state
        self.__shared = {}
        self.__global = {}



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
                                    r.updateQuery(i)
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
                            r.updateQuery(i)

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
                y = yaml.load(obj, Loader=yaml.SafeLoader)
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

    def updateQuery(self, o: dict):
        for r in self.reqs:
            r.updateQuery(o)

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
        self.querys={}

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
        r.querys = clone(self.querys)
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


    def updateQuery(self, o: dict):  # merge query
        query = o.get("query", {})
        self.parent._assertType("query", query, [dict])
        if query is not None:
            # dict_merge(self.querys, query)
            for k,v in query.items():
                if v is None:
                    self.querys[k]=None
                else:
                    if type(v)==list:
                        self.querys.setdefault(k,[]).extend(v)
                    else:
                        self.querys.setdefault(k,[]).append(v)



    def __repr__(self):
        l = []
        l.append("<Req %s: %s>" % (self.method, self.path))
        if self.ifs:
            l.append("\tif: %s" % (self.ifs))
        if self.headers:
            l.append("\theaders: %s" % (self.headers))
        if self.querys:
            l.append("\tquery: %s" % (self.querys))
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
        self, gscope: Env, http=None, outputConsole=OutputConsole.MINIMAL
    ) -> newcore.env.Exchange:

        # create a dict (newscope) from the cloned old env (gscope)
        scope = dict(gscope.clone())

        # merge the local params in
        dict_merge(scope, self.params)

        # get properties of the request
        method, path, body, headers, querys = self.method, self.path, self.body, self.headers, self.querys
        doc, tests, saves = self.doc, self.tests, self.saves


        # get global timeout
        try:
            timeout = scope.get("timeout", None)  # global timeout
            timeout = timeout and float(timeout) / 1000.0 or None
        except ValueError:
            timeout = None

        # get global proxy
        try:
            proxy = scope.get("proxy", None)  # global proxy (proxy can be None, a str or a dict (see httpx/proxy))
        except :
            proxy = None



        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE

        # transform saves to newsaves
        newsaves=[]
        for d in saves:
            for k,v in d.items():
                newsaves.append( (k,v) )

        # transform tests to newtests
        newtests=[]
        for d in tests:
            k,v=list(d.items())[0]
            newtests.append( (k,v) )

        # ensure content is str
        if body is None:
            body=""
        elif type(body) in [list,dict]: # TEST 972_500 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            body=json.dumps(body)
        elif type(body) == bytes:
            body=newcore.common.decodeBytes(body)
        else:
            body=str(body)


        # CREATE the REAL NEW SCOPE !!!!!!
        newenv=newcore.env.Scope( scope , EXPOSEDS)

        # use global headers and merge them in headers
        gheaders = newenv.get("headers", None)  # global headers
        if gheaders is not None:
            if type(gheaders) == str:
                gheaders = newenv.resolve_all(gheaders)
            else:
                gheaders=dict(gheaders) # clone

            self.parent._assertType("headers", gheaders, [dict])

            # merge current headers in gheaders
            gheaders.update( {k:v for k,v in headers.items()} )
            headers=gheaders

        # execute the request (newcore)
        ex = await newenv.call(method,path,headers,body,newsaves,newtests, timeout=timeout, doc=doc, querys=querys, proxies=proxy, http=http)

        ex.nolimit = self.nolimit   #TODO: not beautiful !!!

        ##/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        ##/\ See "test_070" : need to put a ".scope" in an Exchange
        ##/\ to let the tests works, like in the past ...
        ##/\ (because it's a pertinent test !!!)
        ##/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        if outputConsole=="*OLD*TESTS*":
            ex.scope = dict(newenv)
        ##/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        # get the saved ones
        for saveKey, saveWhat in ex.saves.items():
            self.parent.env.save(saveKey, saveWhat, self.parent.name in ["BEGIN","END"])
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE
        ###################################################################################### NEWCORE

        # =================================================== LIVE CONSOLE
        if outputConsole != OutputConsole.NO:
            allIsOk = all(ex.tests)
            if not (allIsOk and outputConsole == OutputConsole.MINIMAL_ONLYKO):
                print(
                    "*",
                    cy(ex.method),
                    ex.url,
                    "-->",
                    cw(ex.content.decode() if ex.status is None else ex.status),
                )

                if outputConsole == OutputConsole.FULL:
                    display = lambda h: "\n".join(["%s: %s" % (k,v) for k,v in h.items()])

                    if ex.inHeaders:
                        print(padLeft(display(ex.inHeaders)))
                    if ex.body:
                        print(padLeft(prettify(ex.body))) #TODO: prettify
                    print(padLeft("-" * 75))
                    if ex.outHeaders:
                        print(padLeft(display(ex.outHeaders)))
                    if ex.content:
                        print(padLeft(prettify(ex.content)))          #TODO: prettify
                    print(padLeft("-" * 75))

                for t in ex.tests:
                    if ex.status is None:
                        print("  -", t and "OK" or "KO", ":", t.name)
                    else:
                        print("  -", t and cg("OK") or cr("KO"), ":", t.name)
                print()
        # =================================================== LIVE CONSOLE

        return ex




######################################################################################"
## test part (old code)
######################################################################################"


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





class Result:
    forceNoLimit=False

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
            assert buf[:4] == b"RMR3"  # TODO
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
            fid.write(b"RMR3" + zlib.compress(x))
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
                for s in yaml.load(FString(i), Loader=yaml.SafeLoader):
                    if "conf" in s:
                        self.fileSwitches.extend(list(Env(s["conf"]).switches))
            except:
                pass
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        for k, v in penv.items():  # add param's input env into env
            self._r.env[k] = guessValue(v)

        if len(files)==1 and os.path.basename(files[0])==REQMAN_CONF:
            # special case of "reqman.exe reqman.conf"
            self._r.ymls=[""]
        else:
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


def prettify(txt: bytes, indentation: int = 4) -> str:
    assert type(txt)==bytes
    if not txt:
        return ""
    else:
        if type(txt)==bytes:
            txt=newcore.common.decodeBytes(txt)
        else:
            txt = str(txt)
    try:
        return repr(newcore.xlib.Xml(txt))
    except:
        try:
            return newcore.common.jdumps(json.loads(txt), indent=indentation, sort_keys=True)
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
        if rr.forceNoLimit:
            return txt
        else:
            if size and txt and type(txt) in [str,bytes] and len(txt) > int(size):
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
            {{first_path(ex)}}
            <b style="float:right">
                %for x in discover(ex):
                    {{x and (x.content if x.status is None else x.status) or "X"}}
                %end
            </b>
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
{{limit(prettify(x.body),isLimit and LIMIT.BODY)}}</pre>
--> {{x.info}}

<pre>
%for k,v in x.outHeaders.items():
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

    path = hp.path + ("?" + hp.query if hp.query else "") + ('#' + hp.fragment if hp.fragment else "")

    yml = GenRML("GET",path)
    yml.doc = "-Test created for '%(root)s%(path)s'" % locals()
    yml.comment = "- GET: %(root)s%(path)s" % locals()
    yml.tests=[("status",200)]

    return (rc, str(yml)) #generate rml without "query:"


def extractParams(params):
    files, rparams, switches, dswitches = [], [], [], []
    for param in params:
        if param.startswith("--"):
            # reqman param
            p = param[2:]
            if p.startswith("o") or p.startswith("x"):
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
        outputContent=None
        forceNoLimit=False
        for p in rparams:
            if p == "k":
                outputConsole = OutputConsole.MINIMAL_ONLYKO
            elif p == "f":
                forceNoLimit=True
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
            elif p.startswith("x"):
                outputContent = p[1:].strip(":= ")
                if not outputContent:
                    raise RMCommandException("You should provide a var'name with --x:<varname>")
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
            rr.forceNoLimit=forceNoLimit
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

        if outputContent!=None:
            ns=newcore.env.Scope( r._r.env.clone() ,EXPOSEDS)
            try:
                x=ns.get_var(outputContent)
                if x is newcore.env.NotFound:
                    x=None
            except newcore.env.ResolveException:
                x=None

            if type(x) in [list,dict]:
                return json.dumps( x )
            else:
                return x
        else:
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

        print( __usage__ )
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
###############################################################################################

def toYaml(x,idt=2):
    return yaml.safe_dump( x ,default_flow_style=False,encoding='utf-8', allow_unicode=True,indent=idt,sort_keys=False).decode()

def pad(txt,prefix):
    return "\n".join([prefix+line for line in txt.splitlines()])

class GenRML:
    """ class Helper to generate a request to RML string """

    def __init__(self,verb: str,path: str,body=None,headers={}):
        if verb is None: verb="GET"
        verb=verb.upper().strip()
        assert verb in KNOWNVERBS
        assert type(headers) in [list,dict]

        self.verb=verb
        self.path=path
        self.body=body

        self.headers=dict(headers) if type(headers)==dict else {k:v for k,v in headers}

        self.doc=""         # str
        self.comment=""     # str|list
        self.returns=""     # any

        self.tests=[]       # generate special "tests" keyword
        self.params=[]      # generate special "params" keyword

        self.__autoParams=False
        self.__genQuerys=False

    def setGenerateParams(self,v:bool):
        """ generate "params:" statement according presences of <<x>>|{{x}} in path,body,headers & doc"""
        self.__autoParams=v

    def setGenerateQuery(self,v:bool):
        """ generate "query:" statement (new)"""
        self.__genQuerys=v

    def __repr__(self):
        extract=lambda txt: [(key[2:-2],"VALUE") for key in Env().getNonResolvedVars(txt) ]

        if self.__autoParams:
          self.params.extend(extract(self.path))
          self.params.extend(extract(self.doc))
          self.params.extend(extract(self.body))
          for k,v in self.headers.items():
              self.params.extend(extract(v))

        d={}
        if self.__genQuerys:
            o=urllib.parse.urlparse(self.path)
            qs=urllib.parse.parse_qs(o.query)
            o=o._replace(query="")
            d[self.verb] = o.geturl()
            qs = {k: v[0] if len(v)==1 else v for k,v in qs.items()}
        else:
            d[self.verb] = self.path
            qs=None

        d["XXX"]="X-X-X"
        if self.doc: d["doc"]="Re-pl-ac-eT-he-Do-cs"
        if qs: d["query"]=qs
        if self.headers: d["headers"]={k:v for k,v in self.headers.items()}
        if self.body:
          try:
            body=json.loads(self.body)
          except:
            body=self.body

          d["body"]=body
        if self.params: d["params"]={k:v for k,v in self.params}
        if self.tests: d["tests"]=[{k:v} for k,v in self.tests]

        y=toYaml( [d] )
        if self.returns:
          l=[]
          l.append( "# RETURNS:" )
          l.append( pad(toYaml(self.returns),"#   ") )
          y+="\n".join(l)

        if self.comment:
            coms=self.comment.splitlines() if type(self.comment)==str else self.comment
            l=["# "+i for i in coms]
            l.append("#"*80)
            c="\n".join(l)
        else:
            c="#"*80

        y=y.replace("  doc: Re-pl-ac-eT-he-Do-cs", "  doc: |\n%s" % pad( str(self.doc),"    "))
        y=y.replace("  XXX: X-X-X",c)

        yml= "\n%s\n%s\n" % ( "#"*80,y)

        return re.sub(r"\{\{([\w_\-\d]+)\}\}", r"<<\1>>", yml)


if __name__ == "__main__":
    sys.exit(main())
