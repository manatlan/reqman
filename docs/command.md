# The command line

You can pass an many yaml's test files or folders as you want. Reqman will compute a list of tests, and order them according names. So it's a good practice, to prefix file names with numbers. Reqman will ignore files/folders starting with a "." or "_".

And it will run the tests against the first reqman.conf found in the common path, if it exists.

If [reqman.conf](conf.md) contains [switchs](conf.md#switchs), you'll be able to add switchs in your command line.

```
USAGE TEST   : reqman [--option] [-switch] <folder|file>...
USAGE CREATE : reqman new <url>
Version 2.1.0.2
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
    
[switch]     : pre-made 'switch' defined in a reqman.conf
```

## Reqman's options

### p: paralleliz
Will run a "thread" by test's file. It's a lot speeder ;-)

### b: browser
Will open `reqman.html` file in the default browser, after tests.

... will continue to explain new reqman2 features ...
... will continue to explain new reqman2 features ...
... will continue to explain new reqman2 features ...
... will continue to explain new reqman2 features ...
... will continue to explain new reqman2 features ...
... will continue to explain new reqman2 features ...

## Start a new project
There is a special command to start a new project from scratch :

```
$ reqman new https://www.example.com/myapi/v1/test
```

It will create, in the current folder, a (very) basic [reqman.conf](conf.md) and a test file against this url

And you can run test immediatly :
```
$ reqman .
```


## Shebang mode
It's my most loved feature, over reqman1 ;-)

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
(if the file is runned with others files or with options/switch ... reqman will use options/switchs from commandline)

Very handy, to avoid to go in console while coding your test ;-)



