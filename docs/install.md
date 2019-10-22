#Install

## On Windows

Download [reqman.exe](https://github.com/manatlan/reqman/blob/master/dist/reqman.exe)

## On *nix platforms
In a console:
```
$ pip3 install reqman
```
(Will install [PyYAML](https://pypi.org/project/PyYAML/), [httpcore](https://pypi.org/project/httpcore/), [stpl](https://pypi.org/project/stpl/) and [colorama](https://pypi.org/project/colorama/) dependencies)

## From Sources
In a console:
```
$ git clone https://github.com/manatlan/reqman.git
$ pip3 install pyyaml httpcore stpl colorama pytest
$ python3 -m pytest tests/
$ python3 setup.py install
```

