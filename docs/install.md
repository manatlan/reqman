# reqman

## TL;DR

`reqman` is a command line tool to test your http requests. It uses `.req` files, which are simple yaml files, to define your requests and tests.

It's a single file, you can download it here :
[reqman](https://raw.githubusercontent.com/manatlan/reqman/master/reqman)
(Will install [PyYAML](https://pypi.org/project/PyYAML/), [httpx](https://pypi.org/project/httpx/), [stpl](https://pypi.org/project/stpl/) and [colorama](https://pypi.org/project/colorama/) dependencies)

## Installation using pip

You can install it thru pip/pip3, like that:
```
$ pip3 install reqman
```
(it will install dependencies)

Or, if you want to install it manually, you will need to install these dependencies:
```
$ pip3 install pyyaml httpx stpl colorama pytest
```

## IDE Integration

There is a [vscode extension](https://marketplace.visualstudio.com/items?itemName=manatlan.reqman) to add syntax highlighting for `.req` files.
Here is a [video](https://www.youtube.com/watch?v=sO-s_nZ-tA4) of the extension in action.

And there is a [vim plugin](https://github.com/manatlan/reqman.vim) for vim users.
Here is a [video](https://www.youtube.com/watch?v=q-J_q-J_q-A) of the plugin in action.