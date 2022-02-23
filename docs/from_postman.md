# If you came from postman

Don't be afraid ... There is no GUI. The GUI is your file editor (it can be vscode, eclipse, notepad++, ...) as long as it support the [yaml syntax](https://fr.wikipedia.org/wiki/YAML).
And you [can run them directly from your text editor](command.md#shebang-mode), by linking the test file to reqman executable.
It's more natural to copy/paste/duplicate your tests easily.

**reqman** is heavily based on postman concepts :

 * the collection : it can be a yaml file, or a subfolder with reqman's yaml tests. It's up to you to run it with your desired tests. You can organize them as you want.
 * the environment : it's basically the things in your `reqman.conf`. It's the place the common things to all tests : the globals vars, the init's process, the swicthes to change context, ...
 
A base structure folder could be like this :

```
    ├── 10-tests-authent              \
    │   ├── 10-login.yml              |
    │   └── 20-signout.yml            |
    ├── 20-tests-basket               ├- the collection
    │   ├── 10-add-product.yml        |
    │   ├── 20-show-basket.yml        |
    │   └── 30-checkout.yml           /
    reqman.conf                       <- the environment
```
!!! tip
    it's a good practice to suffix files with number, to easily reach them in console with auto-completion in the commandline.

If you want to test the authent/signout :

```
$ reqman 10-tests-authent/20-signout.yml
```
(you type reqman, space, 1 and fire up the autocompletion with tab, and 2 and autocompletion )

If you want to test all your baskets tests :
```
$ reqman 20-tests-basket
```
If you have defined [switches](conf.md#switches) in your `reqman.conf`, and want to test your baskets tests in `prod` environment
```
$ reqman 20-tests-basket -prod
```
if you want to tests all in `prod`
```
$ reqman . -prod
```
## About requests
In postman, it's easy to upload a file in your request, or authentificate your request on AWS, etc ... using the GUI and availables features in postman.

In **reqman** there is no special/dedicated features for theses simples things. BUT there is more : a way to [embed python in yaml's tests](python.md). So, basically, you
can do all that is available in python, in reqman's tests. It gives the ability to do a lot of things, but you will need python knowledgment.

So uploading a file, or compute a signature can be done in 2/3 lines of python code in the yaml.

But don't be afraid, you don't need to use/known python in your tests in 99% cases.
It's just for power users, but it adds the ability to do a lot of complex things.

## About tests

In postman, you can control the response object with javascript (to test the returned status code is 200, or the content-type is json, etc ...).
In **reqman**, this kind of [tests are simple yaml statements](yml_syntax.md#tests), that you describe in your yaml/requests flow. It's really easy to write tests, and allow non-tech people to
write them. (really important to separate the concerns)

The reqman's reporting (in console, or the more detailled exchange in the html output) will sort theses tests with "OK" or "KO" statement, depending of the results.
and display you a summary of the state. If you match, for example: 277/277, you can consider 100% OK. If you match 250/277, there are 27 KO results.

BTW, the command line return a code :

 * 0  : which means 0 KO tests. Everything is OK, 100%
 * x  : the number of failed (KO) tests
 * -1 : there was at least one request that couldn't be executed (timeout, unreachable, error in yaml, ...)

So it's easily scriptable, for example : a reqman cron task can easily send you a SMS, or a mail, to alert you if it fails.

## Conversion

If you want to test : you can [convert](https://reqman-tools.glitch.me/) your exported postman collection.

The tool is not magic :

 * You will loose your structured sub-collections (only the structure, not the requests). Everything is outputed in one flow. It's up to you to copy/paste in your future reqman tests collection.
 * You will need to adapt, according your environment (to resolve global/envs vars)
 * The converter can't reproduce the javascript tests/scripts ... you will need to add them manually.
 
But it's good way to see how it will work for you, by copying/pasting requests in your yaml's tests files.

BTW, in normal case, this [tool](https://reqman-tools.glitch.me/) will help you to create your first tests using a [swagger/openapi specifications](https://swagger.io/specification/).

!!! info
    this [tool](https://reqman-tools.glitch.me/) is only available online (because it's not finished). But will release it on github, when done.