# Reqman

**Reqman** is a [postman](https://www.getpostman.com/) killer. It shares the same goal, but without GUI ... the GUI is simply your favorite text editor, because requests/tests are only simple yaml files. **Reqman** is a command line tool, available on any platforms.

<iframe width="640" height="460" src="https://www.youtube.com/embed/ToK-5VwxhP4?autoplay=1&loop=1&playlist=ToK-5VwxhP4&cc_load_policy=1" frameborder="0" allow="accelerometer; autoplay; loop; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

All configurations is done via simple yaml files, editable with any text editors. Results are displayed in console and in an html output. It's scriptable, and can be used as a daemon/cron task to automate your tests.

!!! info
    Here is an [online converter of swagger/openapi3, OR postman collections](https://reqman-tools.glitch.me/) to reqman's tests !


**Reqman** shines with:

 * Tests http apis / website
 * Non regression tests
 * Automatic tests
 * Batch http process
 * TDD of apis

**Reqman**'s history : postman is cool, but is not adapted to non-tech people, to implement "tests" (need JS knowledge), when things going harder. Btw, it (the free version) is a mess when you want to share your tests in a source control system. And the lack of a headless mode (#), for scripting is problematic. So there were room for **reqman**. With **reqman** you can put your complex things in reqman.conf, and let your tests be simple, and easily maintenable by non-tech people. (#: nowadays, it exists, but it's complex to setup)

**Reqman**'s name is a joke, a contraction of "request" and "man" ... and it can do a lot more than just POST requests ;-)

!!! info
    The reqman2, is a full rewrite of reqman1, with new features as [Dual Mode](command.md#dual-mode) and [RMR file](command.md#rmr-file).
