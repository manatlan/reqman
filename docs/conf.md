# Using a reqman.conf

It can be very useful to share common things in a single place : the `reqman.conf` is here for that !
It's not needed: **reqman** can work without it. But if you need to share things between many files ; it's the place.

Basically, it's a yaml file, which is a dictionnary of key:value.

It is useful :

  * to define some globals parameters (and root, timeout, headers, ...)
  * to declare some switches for command line.
  * to share some global procedures between yaml's files.
  * to share some global [python params/methods](python.md) between yaml's files.

## Define some globals parameters

In the `reqman.conf`, you can create as many global parameters as you want, in a dict form ;-)

Example:

```yaml
myValue: 42

myList:
  - 12
  - "hello"
```

In fact you can create as many params as you want, but you should avoid to name your params with the reserved keywords :
`root`, `timeout`, `headers`, `switches`, `BEGIN` & `END` whose have a special function.

### "root"

It's the root path, which is used as prefix when a request use a relative path

```yaml
root: https://example.com
```

tip: this var can be overriden in a "params"/"foreach" statement.

!!! info
    the `root`'s content is auto-prepended on request's path which doesn't have a scheme/protocol (http(s)://, ws(s):// ...)

### "timeout"
It's the max time in milliseconds to wait the response

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

### "verify", "cacert" and "cert"
Reqman keeps its historical HTTPS behavior by default: SSL verification is disabled unless configured.

Enable server certificate verification using the default trusted CA bundle:

```yaml
verify: true
```

Use a custom CA bundle, equivalent to curl's `--cacert`:

```yaml
cacert: ca.pem
```

Use a PEM client certificate, equivalent to curl's `--cert`:

```yaml
cert: client.pem
```

Use a separate PEM client certificate and key, equivalent to curl's `--cert` and `--key`:

```yaml
cert:
    cert: client.pem
    key: key.pem
```

Encrypted private keys can set `password`:

```yaml
cert:
    cert: client.pem
    key: key.pem
    password: secret
```

You can also group SSL options under `ssl`. This is preferred when setting a client key because `key` is otherwise a generic top-level name:

```yaml
ssl:
    verify: true
    cacert: ca.pem
    cert: client.pem
    key: key.pem
```

Relative certificate paths are resolved from the folder containing `reqman.conf` or the scenario file.

Full TLS example in a `reqman.conf`:

```yaml
root: https://api.example.com
timeout: 10000

headers:
    accept: application/json
    content-type: application/json

ssl:
    # Optional when cacert is set; shown here to make verification explicit.
    verify: true

    # Verify the server certificate against this private CA bundle.
    cacert: certs/ca.pem

    # Send this client certificate/key pair for mutual TLS authentication.
    cert: certs/client.pem
    key: certs/client.key

    # Optional: only needed when the private key is encrypted.
    password: secret
```

With this configuration, a scenario can use relative paths and inherit the TLS settings:

```yaml
- GET: /health
  tests:
    - R.status: 200

- POST: /schemas
  body:
    name: customer
  tests:
    - R.status: [200, 201]
```

## Declare switches for command line
### "switches"
Switches are a reqman's feature, to let you override default param with command line switches.

Here is a simple reqman.conf:
```yaml
root: https://example.com

switches:
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

In fact, every things declared under the `goog` key will override things which are declared at the root of the file.

You can combine as many switches as you want ...

BTW, you can add a 'doc' statement, which will appear in [command line usage](command.md), like this:
```yaml
root: https://example.com

switches:
    goog: 
        doc: "to test google ;-)"
        root: https://google.com

```
!!! info
    Previous Reqman versions used `switchs` statement (a spelling error). But now, the two syntax are supported ... but prefer `switches` (it's more compliant ;-))

## Declare procedures

As you can declare a procedure in a yaml's test file, you can declare it in the reqman.conf. So every test's files can use it.

But there are two special procedures: `BEGIN` & `END`

### "BEGIN" procedure

It's a special procedure, which can be declared in reqman.conf only, and is auto-called at the beginning of all tests.
It can be useful to obtain an oauth2 token bearer, initiate some things, ...

### "END" procedure

It's a special procedure, which can be declared in reqman.conf only, and is auto-called at the end of all tests.
It can be useful to clear some things after all tests, ...
