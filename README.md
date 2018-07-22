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
it will install the _reqman.py_ script in your path (perhaps, you'll need to Add the path _~/.local/bin_ to the _PATH_ environment variable.)

If you are on microsoft windows, just download [reqman.exe](https://github.com/manatlan/reqman/tree/master/dist/reqman.exe), and add it in your path.

## Getting started : let's go

Imagine that you want to test the [json api from pypi.org](https://wiki.python.org/moin/PyPIJSON), to verify that [it finds me](https://pypi.org/pypi/reqman/json) ;-)
(if you are on windows, just replace _reqman.py_ with _reqman.exe_)

You can start a new project in your folder, like that:

    $ reqman.py new https://pypi.org/pypi/reqman/json
It's the first start ; it will create a conf file _reqman.conf_ and a (basic) test file _0010_test.rml_. Theses files are [YAML](https://en.wikipedia.org/wiki/YAML), so ensure that your editor understand them !
(Following 'new' command will just create another fresh rml file if a _reqman.conf_ exists)

Now, you can run/test it :

    $ reqman.py .
It will scan your folder "." and run all test files (*.rml or *.yml) against the _reqman.conf_ ;-)

It will show you what's happened in your console. And generate a _reqman.html_ with more details (open it to have an idea)!

If you edit the _reqman.conf_, you will see :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
```

the **root** is a _special var_ which will be prependded to all relative urls in your requests tests.
the **headers** (which is a _special var_ too) is a set of _http headers_ which will be added to all your requests.

Change it to, and save it:

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)

test:
    root: https://test.pypi.org
```

Now, you have created your first _switch_. And try to run your tests like this:

    $ reqman.py . -test
It will run your tests against the _root_ defined in _test_ section ; and the test is KO, because _reqman_ doesn't exist on test.pypi.org !
In fact; all declared things under _test_ will replace those at the top ! So you can declare multiple environments, with multiple switchs ! 

But you can declare what you want, now edit _reqman.conf_ like this :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
package: reqman

test:
    root: https://test.pypi.org
```

You have declared a _var_ **package** ! let's edit the test file _0010_test.rml_ like this :

```yaml
- GET: /pypi/<<package>>/json
    tests:
    - status: 200
```

Now, your test will use the **package** var which was declared in _reqman.conf_ ! So, you can create a _switch_ to change the package thru the command line, simply edit your _reqman.conf_ like that :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
package: reqman

test:
    root: https://test.pypi.org

colorama:
    package: colorama
```

Now, you can check that 'colorama' exists on pypi.org, like that :

    $ reqman.py . -colorama
And you can check that 'colorama' exists on test.pypi.org, like that :

    $ reqman.py . -colorama -test

As you can imagine, it's possible to make a lot of fun things easily. (see a more complex [reqman.conf](https://github.com/manatlan/reqman/blob/master/examples/reqman.conf))


Now, you can edit your rml file, and try the things available in this [tuto](https://github.com/manatlan/reqman/blob/master/examples/tuto.yml).
Organize your tests as you want : you can make many requests in a rml file, you can make many files with many requests, you can make folders which contain many rml files. _Reqman_ will not scan sub-folders starting with "_" or ".".

_reqman_ will return an _exit code_ which contains the number of KO tests : 0 if everything is OK, or -1 if there is a trouble (tests can't be runned) : so it's easily scriptable in your automated workflows !

Use and abuse !


