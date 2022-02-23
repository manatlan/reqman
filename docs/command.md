# The command line

You can pass as many yaml's test files or folders as you want. Reqman will compute a list of tests, and order them according names. 

!!! tip
    It's a good practice, to prefix filenames with numbers. 

!!! tip
    Reqman will ignore files/folders starting with a "." or "_".

And it will run the tests against the first `reqman.conf` found in the common path (ascending), if it exists.

If [reqman.conf](conf.md) contains [switches](conf.md#switches), you'll be able to add switches in your command line.


## Reqman's usage

 * `options` are internal features of **reqman**, and starts with 2 "-".
 * `switches` are exposed features of your `reqman.conf`, and starts with 1 "-". (it can start with 1 '+', to enable [Dual Mode](#dual-mode)). It's the common place, to set your environment for your tests.

!!! info
    NEW(since 2.2.4.0) : there is a way to declare var in environment from command line
    
    Example:
    ```$ reqman . var:value```
    
    will declare the var named 'var' valued with content 'value' in the env.
      


```
USAGE TEST   : reqman [--option] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version 3.0.4
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
        --s        : Save RMR file (timestamped)
        --S        : Save RMR file (reqman.rmr)
        --r        : Replay the given RMR file in dual mode
        --i        : Use SHEBANG params (for a single file), alone
        --f        : Force full output in html rendering
        --j:name   : Set a name for the junit-xml output file
        --j        : Generate a junit-xml output file (reqman.xml)
        --x:var    : Special mode to output an env var (as json output)
```
### --k: only ko
Will output, in console, only the failed tests (DEPRECATED)

### --p: paralleliz
Will run a "thread" by test's file. It's a lot speeder ;-)

### --b: browser
Will open `reqman.html` file in the default browser, after tests.

### --o: html output file
If you need to set a name for the html output file, you can do it with that.
(it can be useful when reqman is scripted, and you need to produce different html result)
By default, the file will alwasys be named `reqman.html`.

Examples:

`$ reqman . --o:mytests.html`

The html output file will be named 'mytests.html'

`$ reqman . --o`

It's a special case, when you don't want a html result.

!!! info
    In that case : the full http exchange is outputed in the console.
  
### --s: Save a RMR file
Save a [RMR file](#rmr-file) for later use
The filename is timestamped

### --S: Save a RMR file
Save a [RMR file](#rmr-file) for later use
The filename will be "reqman.rmr"

### --r: Replay a RMR file
Replay a [RMR file](#rmr-file)
(new feature in reqman2)

### --f: force full output in html
To minimize html'filesize. Big output is truncated. If you want to have the full output, you can pass this option.

### --j: generate junit-xml output
With this option, you can tell to reqman to output a "reqman.xml" file. Can be used with Jenkins’ or Bamboo’s pretty graphs.
(This file is computer readable)

### --j:xxxx: generate junit-xml output
Same as "--j", but you can set a filename.

Example:

`$ reqman . --j:mytests.xml`

### --x:xxxx: output an internal var
Same as "--j", but you can set a filename.

Example:

Imagine that you have a test, which create/save a var named "myresult"
With this option, you can output its content in stdout with `$ reqman . --x:myresult`


## Start a new project
There is a special command to help you to start a new project from scratch :

```
$ reqman new https://www.example.com/myapi/v1/test
```

It will create, in the current folder, a (very) basic [reqman.conf](conf.md) and a test file against this url

And you can run test immediatly (in current folder):
```
$ reqman .
```


## Shebang mode
It's my most loved feature, over reqman1 ;-)

It brings the power of the shebang's linux on windows platforms.

Very useful in a text editor : just configure your editor to run the edited yaml file against reqman executable. And if you run a single file, without any parameters. Reqman will look at the shebang, and use the parameters.

```yaml
#!/usr/local/bin/reqman --b -prod
- GET: /<<path>>
  params:
    path: "hello"
```
or
```yaml
#! --b -prod
- GET: /<<path>>
  params:
    path: "hello"
```

Will run the file, with `prod` switch, and open the html output in the default browser ...
(if the file is runned with others files or with options/switches ... reqman will use options/switches from commandline)

Very handy, to avoid to go in console while coding your test, from your editor ;-)

## Dual mode
It let you compare the html results of two environments switches ! To enable dual mode, you will need to pass switches prefixed by '`-`' and '`+`'.

Imagine the following reqman.conf
```yaml
root: http://localhost

switches:
  env1:
    root: https://env1.example.com
  env2:
    root: https://env2.example.com
```
You can compare the dual execution tests, by using :
```
$ reqman . -env1 +env2
```
It will produce an html output file where you could compare, side by side, the execution
of your tests on each environment, in one shot. Very handy to spot problems ;-)

!!! info
    Tests are executed in parallel, to save times ;-)

!!! info
    You can add as many swithes as you want. Those with "-" refer to the left one, those with "+" refer to the right one.

!!! info
    If you don't mix '`-`' and '`+`' you will be in single mode only. You need to mix them to fire up dual mode. (adding just '`+`' switches (without '`-`' switches), you will be in single mode only)


## RMR file
A **RMR file** is a saved state of all requests/tests results. It's an "image"
of a test suite results, at a given time. RMR means "ReqMan Results".

It's a reqman's feature which lets you :

 * save the state
 * replay the tests (same context)
 * compare the states
 * share a test suite (one file : the rmr), without sharing the yamls/reqman.conf.

!!! info
    Technically, it's the resulting reqman objects which are just zipped and saved in a file (pickle), for later use.

### Save the state
Just use the option `--s`
```
$ reqman . --s
```
It will execute the tests, in a regular way ... and will save a rmr file (timestamp named)

!!! tip
    At anytime, you can see the content of a RMR file, by calling `$ reqman <yourfile>.rmr`
    It will just regenerate the `reqman.html` file, with the content of the RMR.

### Replay the rmr (same context)
Just use the option `--r` by giving the rmr filename

```yaml
$ reqman --r 191215_1706.rmr
```

In that case : it replays the tests, and will save a html file in dual mode : 
the previous state (left one) VS a current state (right one)

It will replay the tests with the given switches when it was produced ! Same tests, same context ... but at a different time.

!!! info
    Very useful for "non regression tests" (TNR)

!!! warning
    When using `--r`, it's not possible to add swicthes to commandline ! The `--r` is just for replaying the same tests, to see a fresh version in Dual mode.


### Tests the rmr

As the RMR is a file containing all executed tests. It's possible to use it, as base tests, for tests in others contexts.
Just pass the rmr file to the command line, as you give yaml, and add swicthes.

!!! tip
    Note that, if you don't add switches, it will just regenerate the output html. (to see the content)

#### In another context
You can change the context, by providing switches prefixed by "`-`". It will replay the tests from the rmr, in the context, defined by your "`-`" swithes.
It will ouput an html in single mode.

#### With another context, in dual mode
You can start a dual mode tests, by providing switches prefixed by "`+`". It will replay the tests from the rmr, in the context, defined by your "`+`" swithes.
It will ouput an html in dual mode : the original tests from the RMR VS the fresh ones in the new context.

### Share a test suite
So, the rmr file can be shared with your users. They couldn't change the tests, the order, ... But the will be able
to tests it without dealing with yaml, subfolders or reqman.conf.

To see the given state (what they should have)
```
$ reqman state.rmr
```

To test the rmr in another context
```
$ reqman state.rmr -context1
```

To compare the rmr with another context(2)
```
$ reqman state.rmr +context2
```

To compare the rmr, in a fresh state, with another context(2)
```
$ reqman state.rmr -context1 +context2
```

!!! info
    Note, that it's the same syntax as classic calls, with yaml or subfolders in place of "state.rmr".



