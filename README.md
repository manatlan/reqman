# reqman
Reqman is the postman killer ;-)

Create your http(s)-tests in simple yaml files, and run them with command line, against various environments.

**Features**
   * Light (simple file, 200 lines of code)
   * Powerful (at least as postman free version)
   * Variable pool
   * Environment aware (switch easily)
   * https/ssl ok
   * oauth2 simple
   * tests are simple (no code !)
   * headers inherits
   * tests coverage
  
**and soon**
   * html tests renderer (with request/response contents)
   * encoding aware (at least : utf8/cp1252)
   * cookie jar
   * more http verbs
   * create/re-use variables
   * tests inherits
   * doc ;-)
   * python3 ?

**Example**

    $ reqman.py *.yml
Will run all tests in availables yml files

    $ reqman.py example
Will run all yml files in the folder example

**reqman** can use a [reqman.conf](/example/reqman.conf) (which is a yaml file too), to store key/value variables, which can be very handly for the tests ;-). **reqman** will use the first _reqman.conf_ available in the path. Variables will be automatically loaded, and fully available is the tests.

**... MORE TO COME ...**
