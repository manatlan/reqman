Here, there will be more "Real tests"
!!! News tests will be in "realtests" !!!

python3.7 -m pytest tests                                                     --> official tests ;-)
python3.7 -m pytest --cov-report html --cov=reqman tests/test_realtests.py    --> 89% cov currently
python3.7 -m pytest --cov-report html --cov=reqman tests                      --> 97% cov currently
