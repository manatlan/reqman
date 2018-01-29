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

**... MORE TO COME ...**
