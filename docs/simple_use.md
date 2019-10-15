# Simplest use

Create a yml file (ex: `test.yml`)

```yaml
- GET: https://github.com/manatlan/reqman
  tests:
    - status: 200
```

And run it with reqman, in console
```
$ reqman test.yml
```

The console should prints:
```
$ reqman test.yml 
TEST: test.yml
* GET https://github.com/manatlan/reqman --> 200
  - OK : status = 200

RESULT: 1/1 (1req(s))
```

Reqman has called the url and tested that HTTP status == 200, it has generated a `reqman.html` which contains more details about the http exchange, and it returned a RC code == 0 (no test errors)



