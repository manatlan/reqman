## Reqman language Syntax

A reqman's file tests, is a YAML file, endings with ".yml" or ".rml" (ReqMan Language).

Its content is a list of statements. There are 4 types of statements :

 * An http request
 * A Procedure's declaration
 * A call procedure
 * A break statement

**reqman** brings its own substitution mechanism. In many places (value side), you can create vars (`{{a_var}}` or `<<a_var>>`), 
which will be substituted at runtime using [local params](#params), [global params](conf.md#define-some-globals-parameters) or [saved ones](#save)

(since 3.2.0 version : you can use your environments vars (dotenv compliant) too !)

### An HTTP Request
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
Let you add a 'body' in your POST/PUT/... statements ;-)

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
Let you add input's 'headers' in yours statements. 

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

**reqman** provides you special syntax to let you write easily tests on complex content:

 * basic tests: tests around http response (status, headers, content)
 * json tests: tests around http response as a json object
 * xml tests: tests around http response as a xml object

Obviously, you can mix all this kind of tests ^^

#### basic tests

Basic tests are:

  * test a http response status, with keyword `status`
  * test a http response header, with the desired headers
  * test the http response content, with keyword `content`

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3, "list":[42,43]}}
  tests:
    - status: 200
    - content-type: application/json    # test a response header
    - content:  "result"                # ensure that the global response contains text "result"
    - content:  "list"                  # ensure that the global response contains text "list"
```
Here, there are 4 tests.

If you want to tests multiple values, you can add them in a yaml's list, like this :
```yaml
- GET: /returnJson
  tests:
    - status: 
          - 200
          - 304
```
This test will be "OK", if returned status is 200 or 304.

or simpler/shorter :
```yaml
- GET: /returnJson
  tests:
    - status: [200, 304]
```
as json is a subset of yaml ;-)


#### json tests

`json` is a special keyword, which will be populated with the http response content. Only useful, when http
response is *json* content. (if it's not the case, all tests are `null`)

You can navigate in the json object model, with a simple dot notation, like this:

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3, "list":[42,43]}}
  tests:
    - status: 200                       # a basic test
    - json.result.content: "ok"
    - json.result.content: <<myValue>>  # ensure that the content is equal to myValue param
    - json.result.content: . != "ko"
    - json.result.content.size: 2       # test size of the string
    - json.result.size: 2               # test size of the dict
    - json.result.value: . > 3
    - json.result.value: . <= 4
    - json.result.list.size: 2          # ensure the list contains 2 values
    - json.result.list.0: 42            # refer to the first item in the list
    - json.result.list.1: 43            # refer to the second item in the list
    - json.result.list.-1: 43           # refer to the last item in the list
```
!!! info
    the `.size` is a special key, to compute the size of the object


#### xml tests

Since reqman>=2.3.0, xml/xpath is supported too (yet!).

`xml` is a special keyword, which will be populated with the http response content. Only useful, when http
response is (valid) *xml* content. (if it's not the case, all tests are `null`)


```yaml
- GET: https://manatlan.com/sitemap.xml
  tests:
    - status: 200                              # a basic test
    - xml.//url/loc.0: https://manatlan.com/    # ensure that the first *url/loc* is the good url
    - xml.//url.size: . > 10                   # ensure that there are more than 10 urls.
```

!!! info
    * Syntax could be `xml.xpath[.size]`, where `xpath` is a valid xpath expression 
      (ns clark notation not accepted).
    * The **xpath expression always returns a list** : so you can apply the `.size`, to compute the size of the list.
      Or index an element, with the dot notation (ex: "xml.//url/loc**.0**" -> the first one)
      
!!! important
    Currently, you can't use the char "." in the xpath expressions ... will be fixed in next releases !




### "doc"

It's optionnal. It let you describe your test ... This doc will be in the html reqman's output.

```yaml
- GET: /test 
  doc: "Just a test on <<root>> !"
```
Yes, you can use var substitutions in `doc` !

### "params"

It let you set local parameters in your statement, in a dict form.

```yaml
- GET: /<<path>>
  params:
    path: "hello"
```
`<<path>>` is substituted by the value of the param `path`.

### "save"
It lets you save parameters for later use. Theses parameters are only available in the current yaml tests. Only thoses saved in the `BEGIN` procedure will be shared with all test files.

#### Save all the response

It's the way to create parameters based on results. The created param will be available in the current file test, for the following requests.

!!! info
    Thoses created in a [global's procedure (in reqman.conf)](conf.md#declare-procedures), will be available in all tests files.

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: allJson
```
Now, you can use 'allJson' in following statements

#### Save a partial response

```yaml
- GET: /returnJson  # return {"result":{"content":"ok","value":3.3}}
  save: 
    mycontent: <<json.result.content>>
```
Now, you can use 'mycontent' in following statements

!!! tip
    * While saving partial response, you can applying [python transformations](python.md) on saved content.

Here, it's a `json` partial content which is saved, but it could be a `xml` partial content, like this :

```yaml
- GET: /returnXml
  save: 
    mycontent: <<xml.//*:myNode[first()]>>
```


### "foreach"
It let you repeat your statement, with a list of dict.

```yaml
- GET: /test/<<value>>
  foreach:
    - value: 1
    - value: 2
    - value: 3
```
Will make 3 requests. BTW, it's the same thing as :

```yaml
- GET: /test/1
- GET: /test/2
- GET: /test/3
```
!!! info
    You can use only one `foreach` per statement. But if you need nested `foreach` you can do it using [nested call statements](#a-call-procedure).



