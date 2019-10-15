

## Reserved words
### HTTP VERB
Known HTTP verbs : "GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS", "TRACE", "PATCH", "CONNECT"

```yaml
- OPTIONS: /hello
- HEAD: /hello
- GET: /hello
```

### "body"

```yaml
- POST: /hello
  body: "I'm the body"
```


### "headers"

```yaml
- POST: /hello
  body: "I'm the body"
  headers:
    content-type: text/plain
    x-hello: it's me
```


### "tests"

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  tests:
    - status: 200
    - content-type: application/json    # test a response header
    - json.result.content: "ok"
    - json.result.content: . != "ko"
    - json.result.content.size: 2       # test size of the string
    - json.result.size: 2               # test size of the dict
    - json.result.value: . > 3
    - json.result.value: . <= 4
    - content:  "result"                # ensure that the global response contains text "result"
```


### "doc"

```yaml
- GET: /test 
  doc: "Just a description which is displayed in the html output for this request"
```


### "params"
```yaml
- GET: /<<path>>
  params:
    path: "hello"
```


### "save"

#### Save all the response

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: allJson
```
Now, you can 'allJson' in following requests

#### Save a partial response in a new param 'rcontent'

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: 
    rcontent: <<json.result.content>>
```
now, you can 'rcontent' in following requests

### "foreach"

```yaml
- GET: /test/<<value>>
  foreach:
    - value: 1
    - value: 2
    - value: 3
```
Will make 3 requests


### "call"

```yaml
- MyProcedure:
    - POST: /test
      body: <<value>>

    - GET: /test
      tests:
        - content: <<value>>

- call: MyProcedure
  params:
    value: 1
```


## Reserved params:
### "root"

It's the root path, which is used as prefix when request use absolute path

```yaml
- GET: /test
  params:
    root: https://example.com
```

it's better to define it in the reqman.conf


### "timeout"
It's the max time in ms to wait the response

```yaml
- call: MyProcedure
  params:
    timeout: 100  #100ms max
```

it's better to define it in the reqman.conf


## In reqman.conf only:
### "headers"
Global `headers` for all tests

### "tests"
Global `tests` for all tests (DEPRECATED (useless?))

### "switchs"


### "BEGIN" (procedure)

It's a special procedure, which can be declared in reqman.conf only, and is called at the beginning of all tests.
It can be useful to obtain an oauth2 token bearer, initiate some things, ...

### "END" (procedure)

It's a special procedure, which can be declared in reqman.conf only, and is called at the end of all tests.
It can be useful to clear some things after all tests, ...