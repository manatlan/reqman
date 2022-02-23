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

![screenshot](https://cdn.glitch.com/37af6816-a1e5-40da-8fe1-6b484d7f74c5%2Foutput.png?v=1576408641247)

What's happening ?

* Reqman has requested the url
* It has tested that HTTP status == 200
* It summarizes the tests: 1/1 ... one test OK over one test (Displayed in green)
* it has generated a `reqman.html` file which contains more details about the http exchange,
* And it returned a RC code == 0 (no test errors, else will be the number of failed tests, or -1 if error)



