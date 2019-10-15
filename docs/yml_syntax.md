## Reqman language Syntax

A reqman's file tests, is a YAML file, endings with ".yml" or ".rml" (ReqMan Language).

Its content is a list of statements. There are 4 types of statements :

 * A http request
 * A Procedure's declaration
 * A call procedure
 * A break statement


### A HTTP Request
This kind of statement, should contain ONE HTTP VERB, in uppercase (Known HTTP verbs : "GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS", "TRACE", "PATCH", "CONNECT")

```yaml
- GET: /hello
- OPTIONS: /hello
- HEAD: /hello
```

And it's generally completed with [additionnal keywords](yml_syntax.md#additionnal-keywords)


### A Procedure's declaration
This statement declare a procedure which can be only called by a "call statement".

Here is the declaration of a procedure `MyProcedure`:

```yaml
- MyProcedure:
    - GET: /hello1
    - GET: /hello2
```
The content of the procedure is a list which can contains the 4 types of statements.

Note : Without a call statement : this file does nothing ...

### A call procedure
This statement let you call a procedure.
```yaml
- call: MyProcedure
```
or

```yaml
- call: 
    - MyProcedure1
    - MyProcedure2
```

And it's generally completed with [additionnal keywords](yml_syntax.md#additionnal-keywords)


### A 'break' statement
This statement is only useful, when you are working on a test file, it lets you break the process. So you can edit your statements step by step.

```yaml
- GET: /hello1
- break
- GET: /hello2
- GET: /hello3
```
In this case ^^; only the first request is called ... The others are simply ignored.


## Additionnal keywords

Theses keywords can be added on request or call statements, to complete the statement.

### "body"
Let you add a 'body' in your POST statements ;-)

```yaml
- POST: /hello
  body: "I'm the body"
```

```yaml
- POST: /hello
  body: {"key":12, "value":"hello"}
```

```yaml
- POST: /hello
  body:
    key: 12
    value: "hello"
```
Body described in yaml syntax, will automatically converted in json. The latest 2 examples are the same.

### "headers"
Let you add 'headers' in yours statements. 

```yaml
- POST: /hello
  body: "I'm the body"
  headers:
    content-type: text/plain
    x-hello: it's me
```

If there are global or inherited headers, you can override them, by setting them to `null`, like that:

```yaml
- myproc:
    - POST: /hello
      body: "I'm the body"
      headers:
        content-type:       # leave empty, will not send the content-type from the caller
        x-hello: it's me

- call: myproc
  headers:
     content-type: application/json

```
Header's keys are case insensitive.

### "tests"
Let you add 'tests' in yours statements. 

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3, "list":[42,43]}}
  tests:
    - status: 200
    - content-type: application/json    # test a response header
    - content:  "result"                # ensure that the global response contains text "result"
    - json.result.content: "ok"
    - json.result.content: . != "ko"
    - json.result.content.size: 2       # test size of the string
    - json.result.size: 2               # test size of the dict
    - json.result.value: . > 3
    - json.result.value: . <= 4
    - json.result.list.0: 42            # refer to the first item in the list
    - json.result.list.1: 43            # refer to the second item in the list
    - json.result.list.-1: 43           # refer to the last item in the list
```


### "doc"

```yaml
- GET: /test 
  doc: "Just a description which is displayed in the html output for this request on <<root>> !"
```
Yes, you can use var substitutions in `doc` !

### "params"
```yaml
- GET: /<<path>>
  params:
    path: "hello"
```
`<<path>>` is substitued by the value of the param `path`.

### "save"
It lets you save parameters for later use. Theses parameters are only available in the current yaml tests. Only thoses saved in the `BEGIN` procedure will be shared with all test files.

#### Save all the response

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: allJson
```
Now, you can use 'allJson' in following statements

#### Save a partial response in a new param 'rcontent'

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: 
    rcontent: <<json.result.content>>
```
Now, you can use 'rcontent' in following statements



### "foreach"
It let you repeat your statement, with a list of dict.

```yaml
- GET: /test/<<value>>
  foreach:
    - value: 1
    - value: 2
    - value: 3
```
Will make 3 requests, it the same things as :

```yaml
- GET: /test/1
- GET: /test/2
- GET: /test/3
```




