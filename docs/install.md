#Install

## On Windows

Download [reqman.exe](https://github.com/manatlan/reqman/raw/master/dist/reqman.exe)

## On *nix platforms
In a console:
```
$ pip3 install reqman
```
(Will install [PyYAML](https://pypi.org/project/PyYAML/), [aiohttp](https://pypi.org/project/aiohttp/), [stpl](https://pypi.org/project/stpl/) and [colorama](https://pypi.org/project/colorama/) dependencies)

!!! info
    Before version<2.2.0.0, reqman used [httpcore/httpx](https://pypi.org/project/httpcore/). Now it uses [aiohttp](https://pypi.org/project/aiohttp/), to preserve mixed cases in http/1.x headers !

## From Sources
In a console:
```
$ git clone https://github.com/manatlan/reqman.git
$ pip3 install pyyaml aiohttp stpl colorama pytest
$ python3 -m pytest tests/
$ python3 setup.py install
```

