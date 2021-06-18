# reqman (3.X)
Reqman is a postman killer ;-)

**Reqman** is a [postman](https://www.getpostman.com/) killer. It shares the same goal, but without GUI ... the GUI is simply your favorite text editor, because requests/tests are only simple yaml files. **Reqman** is a command line tool, available on any platforms.

[Video (1minute)](https://www.youtube.com/embed/ToK-5VwxhP4?autoplay=1&loop=1&playlist=ToK-5VwxhP4&cc_load_policy=1)

All configurations is done via simple yaml files, editable with any text editors. Results are displayed in console and in an html output. It's scriptable, and can be used as a daemon/cron task to automate your tests.

[Documentation](https://reqman-docs.glitch.me/)

[Changelog](https://github.com/manatlan/reqman/blob/master/changelog) !

[Online tool to convert swagger/openapi3, OR postman collections](https://reqman-tools.glitch.me/) to reqman's tests

[DEMO](https://test-reqman.glitch.me)


**Features**
   * Light (simple py3 module, 3000 lines of code, and x3 lines for unittests, in TDD mind ... cov:97%)
   * Powerful (at least as postman free version)
   * tests are simple (no code !)
   * Variable pool
   * can create(save)/re-use variables per request
   * "procedures" (declarations & re-use/call), local or global
   * Environment aware (switch easily)
   * https/ssl ok (bypass)
   * http 1.0, 1.1, 2.0
   * proxy support (thru a reqman.conf var "proxy")
   * headers inherits
   * ~~tests inherits~~
   * ~~timed requests + average times~~
   * html tests renderer (with request/response contents)
   * encoding aware
   * cookie handling
   * color output in console (when [colorama](https://pypi.org/project/colorama/) is present)
   * variables can be computed/transformed (in a chain way)
   * tests files extension : .yml or .rml (ReqManLanguage)
   * generate conf/rml (with 'new' command)
   * can paralleliz tests (option `--p`)
   * versionning
   * NEW 2.0 :
       * rewrite from scratch, a lot stronger & speeder !
       * advanced save mechanisms
       * new switches system
       * a lot of new options (auto open browser, set html filename, compare, ...)
       * ability to save the state, to compare with newer ones
       * ability to replay given tests (rmr file)
       * dual mode : compare switches vs others switches (-env1 +env2) in html output
       * shebang mode
       * better html output
       * fully compatible with reqman1 conf/ymls
       * xml/xpath support tests
       * used as a lib/module, you can add easily your own features (see below)
   * NEW 3.0 : (simple py file -> real python module (multiple files))
        * full rewrite of resolving mechanism (more robust, more maintanable) (the big improvment)
        - "wait:" commands (time expressed in ms)
        * "ignorable vars" (avoid ResolveException, with `<<var?>>`)
        * --f option : to output full exchanges in html output
        * --j && --j:file.xml : to output junit-xml file

**TODO** : need to rewrite this ^^ ;-)

## Getting started : installation

If you are on an *nix platform, you can start with pip :

    $ pip3 install reqman

it will install the _reqman_ script in your path (perhaps, you'll need to Add the path `~/.local/bin` to the _PATH_ environment variable.)

If you are on microsoft windows, just download [reqman.exe (v3)](https://github.com/manatlan/reqman/blob/master/dist/reqman.exe).
 [The old reqman.exe V2, is still there](https://github.com/manatlan/reqman/blob/ac7d96319bf53e08f5a01ff55c54ef820e839fa6/dist/reqman.exe), and add it in your path.
 [The old reqman.exe V1, is still there](https://github.com/manatlan/reqman/blob/reqman1.4.4.0/dist/reqman.exe), and add it in your path.


## Getting started : let's go

Imagine that you want to test the [json api from pypi.org](https://wiki.python.org/moin/PyPIJSON), to verify that [it finds me](https://pypi.org/pypi/reqman/json) ;-)
(if you are on windows, just replace `reqman` with `reqman.exe`)

You can start a new project in your folder, like that:

    $ reqman new https://pypi.org/pypi/reqman/json

It's the first start ; it will create a conf file _reqman.conf_ and a (basic) test file _0010_test.rml_. Theses files are [YAML](https://en.wikipedia.org/wiki/YAML), so ensure that your editor understand them !
(Following 'new' command will just create another fresh rml file if a _reqman.conf_ exists)

Now, you can run/test it :

    $ reqman .

It will scan your folder "." and run all test files (`*.rml` or `*.yml`) against the _reqman.conf_ ;-)

It will show you what's happened in your console. And generate a `reqman.html` with more details (open it to have an idea)!

If you edit the `reqman.conf`, you will see :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)
```

the **root** is a `special var` which will be prependded to all relative urls in your requests tests.
the **headers** (which is a `special var` too) is a set of `http headers` which will be added to all your requests.

Change it to, and save it :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)

switches:
    test:
        root: https://test.pypi.org
```

Now, you have created your first _switch_. And try to run your tests like this:

    $ reqman.py . -test

It will run your tests against the _root_ defined in _test_ section ; and the test is KO, because _reqman_ doesn't exist on test.pypi.org !
In fact; all declared things under _test_ will replace those at the top ! So you can declare multiple environments, with multiple switches !

But you can declare what you want, now edit _reqman.conf_ like this :

```yaml
root: https://pypi.org
headers:
    User-Agent: reqman (https://github.com/manatlan/reqman)

package: reqman

switches:
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

switches:
    test:
        root: https://test.pypi.org

    colorama:
        package: colorama
```

Now, you can check that 'colorama' exists on pypi.org, like that :

    $ reqman . -colorama

And you can check that 'colorama' exists on test.pypi.org, like that :

    $ reqman . -colorama -test

As you can imagine, it's possible to make a lot of fun things easily. (see a more complex [reqman.conf](https://github.com/manatlan/reqman/blob/master/examples/reqman.conf))


Now, you can edit your rml file, and try the things available in this [tuto](https://github.com/manatlan/reqman/blob/reqman1.4.4.0/examples/tuto.yml).
Organize your tests as you want : you can make many requests in a rml file, you can make many files with many requests, you can make folders which contain many rml files. _Reqman_ will not scan sub-folders starting with "_" or ".".

_reqman_ will return an `exit code` which contains the number of KO tests : 0 if everything is OK, or -1 if there is a trouble (tests can't be runned) : so it's easily scriptable in your automated workflows !


# Ability to override reqman's features for your propers needs (reqman>=2.8.1)
Now, it's super easy to override reqman with your own features. Using 'reqman' as a lib/module for your python's code.
You can declare your own methods, to fulfill your specials needs (hide special mechanism, use external libs, ...):
(Thoses real python methods, just needs to respect the same signature as pyhon methods declared in confs.)

```python
import reqman

reqman.__usage__ = "USAGE: reqmanBis ..."   # override usage or not ;-)

@reqman.expose
def SpecialMethod(x,ENV):
    """
    Do what you want ...

    Args:
        'x'   : the input var (any) or None.
        'ENV' : the current env (dict)

    Returns:
        any
    """
    ...
    return "What you need"

if __name__ == "__main__":
    sys.exit(reqman.main())
```

Now, you can use `SpecialMethod` in your scripts, ex: `<<value|SpecialMethod>>` or `<<SpecialMethod>>`!

Use and abuse !

[![huntr](https://cdn.huntr.dev/huntr_security_badge.svg)](https://huntr.dev)
