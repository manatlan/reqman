# reqman
Reqman is the postman killer ;-)

Create your http(s)-tests in simple yaml files, and run them with command line, against various environments.

**Features**
   * Light (simple py file, 300 lines of code)
   * Powerful (at least as postman free version)
   * tests are simple (no code !)
   * Variable pool
   * Environment aware (switch easily)
   * https/ssl ok
   * oauth2 simple
   * headers inherits
   * tests inherits
   * unittests coverage
   * html tests renderer (with request/response contents)
   * encoding aware
  
**and soon**
   * cookie jar
   * create/re-use variables
   * doc ;-)
   * python3 ?
   * postman converter ?

**Example**

    $ reqman.py 
Will run all yml files in current folder (and children folders)

    $ reqman.py *.yml
Will run all tests in availables yml files

    $ reqman.py example
Will run all yml files in the folder example

    $ reqman.py example *.yml yo/my_tests.yml
Will run all yml files in the folder example + all yml files in current folder + the tests in _yo/my_tests.yml_

**reqman** can use a [reqman.conf](/example/reqman.conf) (which is a yaml file too), to store key/value variables, which can be very handly for the tests ;-). **reqman** will use the first _reqman.conf_ available in the path. Variables will be automatically loaded, and fully available is the tests.

There are 3 specials (and optionnals) vars :

    root: http://github.com         # so you can write your tests without full url (ex: "GET: /")
    headers:
        content-type: application/json
    tests:
        - status: 200               # assert the status response is 200 OK
        - content: GitHub           # assert that there will be the strinf "GitHub" in the response content
        - content-type: text/html   # assert the content-type response header will contain "text/html"

**root** : is the root of the call request, needed if you omit the full url in reqman tests

**headers** : is a dict of headers, which will be appended to each requests

**tests** : is a list of mono key/value pair, to test the response, which will test each requests. (2 specials: _status_ for the status, _content_ to test content inside ... others are for headers only !)


## Tests / yml file

It's a yaml file, which can be a list (multiple tests at once), or a dict (just one test).

Here is a yaml, with just one test (a dict):

    GET: /

Here is a yaml, with just multiple tests (a list):

    - GET: /
    - GET: /explore
    
But requests without tests are useless ... see [tests.yml](/example/tests.yml)
For each request you can set theses keys:

**headers** : is a dict of headers, which will be added to this request
**tests** : is a list of mono key/value pair, to test this response. (2 specials: _status_ for the status, _content_ to test content inside ... others are for headers only !)
**body** : which can be plain text or dict yaml or json. It's the content body which will be send to http access.

_headers_ & _tests_ can be surcharged using _reqman.conf_ ! Not _body_ !

And, of course, you can use variables everywhere (if declared in reqman.conf ;-), like this:

    - POST: /authent
      body: login=me&pass={{passwd}}
      headers:
        content-type: application/x-www-form-urlencoded
      tests:
        - status: 200
        - content: you are logged in

or a json example request:

    - POST: /authent
      body:
        login:  me
        pass:   "{{passwd}}"
      headers:
        content-type: application/json
      tests:
        - status: 200
        - content: you are logged in

**... MORE TO COME ...**
