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

The console should print:
```
$ reqman test.yml 
TEST: test.yml
* GET https://github.com/manatlan/reqman --> 200
  - OK : status = 200

RESULT: 1/1 (1req(s))
```

What's happening ?

* Reqman has requested the url
* It has tested that HTTP status == 200
* it has generated a `reqman.html` file which contains more details about the http exchange,
* And it returned a RC code == 0 (no test errors, else will be the number of failed tests, or -1 if error)



