import setuptools
from reqman import __version__

setuptools.setup(
    name='reqman',
    version=__version__,
    entry_points={
        'console_scripts': [
            'reqman = reqman:main',
        ],
    },
    py_modules=["reqman"],
    author="manatlan",
    author_email="manatlan@gmail.com",
    description="Create your http(s)-tests in simple yaml files, and run them with command line, against various environments",
    long_description=open("README.md","r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/manatlan/reqman",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ),
    install_requires=[
          'aiohttp',
          'py-dom-xpath-six',
          'pyyaml >= 4.2b1',
          'stpl >= 1.13.2',
          'colorama',
          "pyjwt",
    ],
)
