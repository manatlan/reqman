# Install repo on your machine

You will need the marvelous [uv](https://docs.astral.sh/uv/) ;-)

Currently, reqman works OOTB with python 3.9, 3.10, 3.11, 3.12, 3.13 & 3.14. But I would like to ensure compatibiliy from 3.9 (for no reasons), so I pinned the 3.9 version, with uv. (there is [github action](https://github.com/manatlan/reqman/actions/workflows/tests.yml) which tests all at each commit)

Here is a recipe to install the dev env from scratch :

    git clone https://github.com/manatlan/reqman
    cd reqman
    uv python pin 3.9
    uv sync --dev
    uv run pytest

And everythings should work fine.

# How to contribute 

Clone the repo, and propose a up-to-date full-working PR ...

## Need help for the tests

tests are currently a "complex beast" ...
And it miss some edge cases ... 
If you find them, feel free to PR them (and I could try to fix them if you can't)

## Need help for the docs

The docs, are managed by [mkdocs](https://www.mkdocs.org/), and all files are in "./docs" folder.

The docs are outdated at max ;-)

But some features, whose doesn't appear in the docs, may be removed soon like (so avoid to describe them):
- all "rmr" things
- side-by-side comparisons
- "if" keyword
- "foreach" will be replaced by a "params" of list

