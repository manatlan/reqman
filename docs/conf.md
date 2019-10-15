# Using a reqman.conf

It can be very useful to share common things in a single place : the `reqman.conf` is here for that !

Basically, it's a yaml file, which is a dictionnary of key:value.

It is useful :

  * to define some globals parameters (root, timeout, headers, ...)
  * to declare some switchs for command line.
  * to share some global procedures between yaml's files.
  * to share some global [python params/methods](python.md) between yaml's files.

## Define some globals parameters

Here are some special parameters, but you can create as many global parameters as you want ;-)

### "root"

It's the root path, which is used as prefix when a request use an absolute path

```yaml
root: https://example.com
```

tip: this var can be overriden in a "params"/"foreach" statement.

### "timeout"
It's the max time in ms to wait the response

```yaml
timeout: 100  #100ms max
```

tip: this var can be overriden in a "params"/"foreach" statement.


### "headers"
Global [headers](yml_syntax.md#headers) for all tests

```yaml
headers:
    content-type: application/json
```

## Declare switchs for command line
### "switchs"
Switchs are a reqman's feature, to let you override default param with command line switchs.

Here is a simple reqman.conf:
```yaml
root: https://example.com

switchs:
    goog: 
        root: https://google.com
```
if you run :

```
$ reqman test.yml
```
it will use `https://example.com` as root var.

if you run :

```
$ reqman test.yml -goog
```
it will use `https://google.com` as root var.

You can combine as many switchs as you want ...

BTW, you can add a 'doc' statement, which will appear in [command line usage](command.md), like this:
```yaml
root: https://example.com

switchs:
    goog: 
        doc: "to test google ;-)"
        root: https://google.com

```


## Declare procedures

As you can declare a procedure in a yaml's test file, you can declare it in the reqman.conf. So every test's files can use it.

But there are two special procedures: BEGIN & END

### "BEGIN" procedure

It's a special procedure, which can be declared in reqman.conf only, and is called at the beginning of all tests.
It can be useful to obtain an oauth2 token bearer, initiate some things, ...

### "END" procedure

It's a special procedure, which can be declared in reqman.conf only, and is called at the end of all tests.
It can be useful to clear some things after all tests, ...


