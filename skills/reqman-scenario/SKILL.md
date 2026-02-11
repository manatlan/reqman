---
name: reqman-scenario
description: Create distinctive, production-grade reqman scenario with high quality. Use this skill when the user asks to build a reqman scenario. Generates creative, polished code (this skill is under construction). (more info https://github.com/manatlan/reqman)
license: Complete terms in LICENSE.txt
---

# Overview

A scenario is a simple YAML file (with ".yml" extension) which describe a dict of key/value.

To test the scenario, user invoke the command ("reqman.exe" on windows ekse "reqman") in a console interface. Reqman will execute all tests (by doing http call) and will output what's happening.

# structure of a reqman scenario

A reqman scenario file is a yaml file, you can comment with yaml comment, line prefixed with '#'.
The first line of the yaml should start with the comment `# -*- coding: utf-8 -*-`

Every key will be a declared var. (vars must be declared before concrete use)

## switch's keys
A key prefixed with "-" is a "switch" (can only be declared at the root of the yaml), when given in reqman cli, will declare all its sub dict[str,str] as vars in the current execution context. 
In reqman cli, if a switch "-test" is declared in "scenario.yml", you can invoke cli like this:
    - "reqman.exe scenario.yml"
    - "reqman.exe scenario.yml -test"

## key `root` is a str.
It's a global property which will be the basepath at each requests, if the request'url is relative.

## key `headers` is a dict[str,str].
It's a global property which will be used as default headers in all requests.

## key `timeout` is a integer
It's a global property which will be used as the default timer (in milliseconds) for each request.
If not specified, default is 60_000 ms.

## key `proxy` is a str/url
It's a global property which will be used as the default proxy for each request


## key `RUN`
"RUN" is a "list of requests".
It's the "list of request" whose will be executed by the reqman cli.
Alternativly, you can create others keys, to contains a "list of requests". And you can call it from the RUN's list, with a call statement in place of a simple request (useful if you need to capitalize a "list of request", to avoid duplication), example:

    ```yaml
    COMMON:
        - GET: /path1
    RUN:
        - call: COMMON
        - GET: /path2
        - call: COMMON
        - GET: /path3
    ```

# A request
A request is a dict
- The first entry should be a HTTP VERB in uppercase, containing a full or relative path (str).
- the second entry could be "doc" (str), to describe the purpose of the request test (it can contains "pattern substitution")
- the third entry could be "headers" (dict[str,str]) to set specific headers on the requests. But by default globals headers are used, you can surcharge them here.
- the 4th can be a "body" key, which can contains the payload as yaml description.
- the 5th entry can be a "tests" key, which contains a list of mono dict. Theses tests will be executed after the request, and permits to valid assertions. Examples:

    - R.status: 200                : assert the http status code is 200
    - R.status: [200, 201]         : assert the http status code is 200 or 201
    - R.json.response.code: "ok"   : assert the output payload is {"response": {"code":"ok"}}
    - R.json.data.text: .!= null   : assert that in the payload {"data":{"text":".."}}, the 'text' exists
    - R.json.data.text: .? "mr"    : assert the payload data.text contains "mr"
    - R.json.data.text: .!= "KO"   : assert the payload data.text is not "KO"
    - R.json.data.text.size: .>3   : assert the payload data.text has more than 3 chars
    - R.json.data.items.size: .>2  : assert the payload data.items (list) has more than 2 items
    - R.json.data.items.2.code: 1  : assert the payload data.items[2].code is 1.
    - R.json.data.items.-1.code: 1 : assert the last items of has a "code" == 1.
    - R.time: .< 10_000            : assert the response is less than 10 seconds
    - R.content: .? "github"       : assert the response text content contains "github"
    
    "R" is an object which contains always the last result of the request (its properties are only status, json, time, headers, content)
    
- a last entry can be "save" (dict[str,str]), where you can create a var which can be reused in the following requests (use only if needed), examples:
    - lastId: <<R.json.items.-1.id>> : create a var "lastId" which contains the last item.id in the "items" list.

## "pattern substitution"
"Pattern substitution" is available, mainly in values, and can be done with {{key}} or <<key>>.

### using python
You can create python method, to make transformation on the fly. You must declare them at the root of the yaml, example:

    ```
    method: |
        return str(x).upper()
    ```
Internally, it declares a method "def method(x:str|None = None) -> str", that you can use them in "pattern substitution", like <<R.json.response.code|method>> or {{R.json.response.code|method}}. Methods are chainables.

