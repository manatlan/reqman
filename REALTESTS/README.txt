Here, there will be more "Real tests" (the "examples" will be removed)
!!! News tests will be in "realtests" !!!

python3.7 -m pytest REALTESTS
python3 -m pytest --cov-report html --cov=reqman tests/test_realtests.py    --> 88% cov currently
python3 -m pytest --cov-report html --cov=reqman tests                      --> 97% cov currently
