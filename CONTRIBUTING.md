# Install repo on your machine

You will need the marvelous [uv](https://docs.astral.sh/uv/) ;-)

Currently, reqman works OOTB with python 3.9, 3.10, 3.11, 3.12, 3.13 & 3.14. But I would like to ensure compatibiliy from 3.9 (for no reasons), so I pinned the 3.9 version, with uv. (there is [github action](https://github.com/manatlan/reqman/actions/workflows/tests.yml) which tests all at each commit)

Reqman should work on windows system (a github action build it automatically) ;-(

Here is a recipe to install the dev env from scratch :

    git clone https://github.com/manatlan/reqman
    cd reqman
    uv python pin 3.9
    uv sync --dev
    uv run pytest

And everythings should work fine.

# How to contribute 

Clone the repo, and propose an up-to-date full-working PR ...

## Need help for the tests

tests are currently a "complex beast" ...
And it (certainly) miss some edge cases ... 
If you find them, feel free to PR them (and I could try to fix them)

## Need help for the docs

The docs, are managed by [mkdocs](https://www.mkdocs.org/), and all files are in "./docs" folder.

The docs are outdated at max ;-)

But some features, whose doesn't appear in the docs, may be removed soon like (so avoid to describe them):

- all "rmr" things (to complex and not as useful as expected)
- side-by-side comparisons (to complex and not as useful as expected)
- "if" keyword (becoz a foreach/params empty as the same effect)
- "foreach" will be replaced by a "params" with list of dict (simpler/kiss)

need to explain/details :

- new scenario mechanism "RUN:" (from v3.5)
- new switch mechanism '-<switch>" in conf or scenar (from v3.5)
- new "python tests statements" (lot better for IA/LLM) (from v3.5)
- "ignorable vars" (things like `<<var?>>`) (from v3.0)
- the "wait" command (really usefull ?) (from v3.0)
- the "break" command (really usefull ?) (from ??)
- the "query" argument for "http step", to setup query params (from ??)
- the xml/xpath features (from v2.0)
- the junit export (from v3.0)
- the shebang mode (from v2.0)
- can be used as a lib/module (from v2.0)


And stop doing references from oldest versions (OSEF!), because docs should reflect the current version (coz it's versionned in the git repo)
The doc should reflect exactly what is working for THIS version.