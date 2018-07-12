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
it will install the _reqman.py_ script in your path.

If you are on microsoft windows, just download [reqman.exe](https://github.com/manatlan/reqman/tree/master/dist/reqman.exe), and add it in your path.

## Getting started : let's go

Imagine that you want to test the [json api from pypi.org](https://wiki.python.org/moin/PyPIJSON), to verify that [it finds me](https://pypi.org/pypi/reqman/json) ;-)
(if you are on windows, just replace _reqman.py_ with _reqman.exe_)

You can start a new project in your folder, like that:

    $ reqman.py new https://pypi.org/pypi/reqman/json
It's the first start ; it will create a conf file _reqman.conf_ and a (basic) test file _0010_test.rml_.

Now, you can run/test it :

    $ reqman.py .
It will scan your folder "." and run all test files (*.rml or *.yml) against the _reqman.conf_ ;-)

It will show you what's happened in your console. And generate a _reqman.html_ with more details (open it to have an idea)!

If you edit the _reqman.conf_, you will see :

    root: https://pypi.org
    headers:
        User-Agent: reqman (https://github.com/manatlan/reqman)

the **root** is a _special var_ which will be prependded to all relative urls in your requests tests.
the **headers** is a set of headers which will be added to all your requests.

Change it to, and save it:

    root: https://pypi.org
    headers:
        User-Agent: reqman (https://github.com/manatlan/reqman)
    
    test:
        root: https://test.pypi.org

Now, you have created your first _switch_. And try to run your tests like this:

    $ reqman.py . -test
It will run your tests against the _root_ defined in _test_ section ; and the test is KO, because _reqman_ doesn't exist on test.pypi.org !
In fact; all declared things under _test_ will replace those at the top ! So you can declare multiple environments, with multiple switchs ! 
(see a more complex [reqman.conf](https://github.com/manatlan/reqman/blob/master/examples/reqman.conf))

You can edit your rml file, and try the things available in this [tuto](https://github.com/manatlan/reqman/blob/master/examples/tuto.yml)


--- CONTINUE HERE ---
--- CONTINUE HERE ---
--- CONTINUE HERE ---
--- CONTINUE HERE ---


