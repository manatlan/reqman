# reqman
Reqman is the postman killer ;-)

Create your http(s)-tests in simple yaml files, and run them with command line, against various environments.
**reqman** is a python3 simple file (need [PyYAML](https://pypi.org/project/PyYAML/) dependency). The [changelog](https://github.com/manatlan/reqman/blob/master/changelog) !

**Features**
   * Light (simple py3 file, 900 lines of code, and x3 lines for unittests, in TDD mind)
   * Powerful (at least as postman free version)
   * tests are simple (no code !)
   * Variable pool
   * can create(save)/re-use variables per request
   * "procedures" (declarations & re-use/call), local or global
   * Environment aware (switch easily)
   * https/ssl ok (bypass)
   * headers inherits
   * tests inherits
   * timed requests + average times
   * html tests renderer (with request/response contents)
   * encoding aware
   * cookie handling
   * color output in console (when [colorama](https://pypi.org/project/colorama/) is present)
   * variables can be computed/transformed (in a chain way)
   * tests files extension : .yml or .rml (ReqManLanguage)
   * generate conf/rml (with 'new' command)
   * versionning

**and soon**
   * doc & examples ;-)
   * postman converter ?

## Getting started : installation

If you are on an *nix platform, you can start with pip :

    $ pip3 install reqman
it will add the _reqman.py_ script in your path.

If you are on microsoft windows, just download [reqman.exe](https://github.com/manatlan/reqman/tree/master/dist/reqman.exe), and add it in your path.

## Getting started : let's go

Imagine that you want to test the [json api from pypi.org](https://wiki.python.org/moin/PyPIJSON), to verify that [it finds me](https://pypi.org/pypi/reqman/json) ;-)

You can start a new project in your folder, like that:

    $ reqman.py new https://pypi.org/pypi/reqman/json
It's the first start ; it will create a conf file _reqman.conf_ and a (basic) test file _0010_test.rml_.

Now, you can run/test it :

    $ reqman.py .
It will scan your folder "." and run all test files (*.rml or *.yml) against the _reqman.conf_ ;-)

It will show you what's happened in your console. And generate a _reqman.html_ with more details !

You can edit your rml file, and try the things available in this [tuto](https://github.com/manatlan/reqman/blob/master/examples/tuto.yml)

You can edit your _reqman.conf_ file, to add some magic ...

--- CONTINUE HERE ---
--- CONTINUE HERE ---
--- CONTINUE HERE ---
--- CONTINUE HERE ---

**reqman** can use a [reqman.conf](https://github.com/manatlan/reqman/blob/master/examples/reqman.conf) (which is a yaml file too), to use key/value variables, which can be very handly for the tests ;-). **reqman** will use the first _reqman.conf_ available in the path. Variables will be automatically loaded, and fully available in the tests.

There are 5 specials (and optionnals) vars :

    root: http://github.com         # so you can write your tests without full url (ex: "GET: /")
    headers:
        content-type: application/json
    tests:
        - status: 200               # assert the status response is 200 OK
        - content: GitHub           # assert that there will be the strinf "GitHub" in the response content
        - content-type: text/html   # assert the content-type response header will contain "text/html"

- **root** : is the root of the call request, needed if you omit the full url in reqman tests
- **headers** : is a dict of headers, which will be appended to each requests
- **tests** : is a list of mono key/value pair, to test the response, which will test each requests (some are specials: _status_ for the status, _content_ to test content inside ... others are for headers only !)
- **BEGIN** / **END** : theses are procedures which will be runned at start, or at end of the tests. (useful to start/end a specific context)


## The Tests / [ry]ml file

It's a yaml file, which can be a list (multiple tests at once), or a dict (just one test).

Here is a yaml, with just one test (a dict):

    GET: /

("GET" is a http verb, always uppercases)

Here is a yaml, with multiple tests (a list):

    - GET: /
    - GET: /explore

But requests without tests are useless ... see [tests.yml](https://github.com/manatlan/reqman/blob/master/examples/tests.yml).


For each request you can set theses keys:

- **headers** : is a dict of headers, which will be added to this request
- **tests** : is a list of mono key/value pair, to test this response. (2 specials: _status_ for the status, _content_ to test content inside ... others are for headers only !)
- **body** : which can be plain text or dict yaml or json. It's the content body which will be send to http access.
- **save** : save response content in a var in the environment (can be reused in next requests)
- **params** : is a dict of params, that can override env params for the current request

_headers_ & _tests_ can be surcharged using _reqman.conf_ (see above) ! Not _body_ !

And, of course, you can use variables everywhere (if declared in reqman.conf ;-), just use {{my_var}} syntax (or alternative syntax <<my_var>>), like this:

    - POST: /authent
      body: login=me&pass={{passwd}}                # plain text urlencoded
      headers:
        content-type: application/x-www-form-urlencoded
      tests:
        - status: 200
        - content: you are logged in

or a json example request:

    - POST: /authent
      body:                                         # will be converted to json
        login:  me
        pass:   "{{passwd}}"                        # escape the string to avoid trouble with yaml syntax (else use the alternative syntax)
      headers:
        content-type: application/json
      tests:
        - status: 200
        - content: you are logged in

## Change the config with command line

It can be very useful to run your tests with various parameters (think various environments). That could be done with "switch" in command line. It use the variable pool of the _reqman.conf_.

So, if you got a _reqman.conf_ like this:

    root: https://github.com

    local:
        root: http://localhost:8080

If you run your tests like this:

    $ reqman.py *.yml

it will use the first "root" var (aka https://github.com)!

If you run your tests like this:

    $ reqman.py *.yml -local

it will use the second "root" var (aka http://localhost:8080) ! (in fact, vars declared under the key _local_ will replace thoses in the first level)

So you can imagine a lot of combinations, because you can add unlimited switchs ;-)


**... MORE TO COME ...**
