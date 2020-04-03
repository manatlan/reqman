Here, there will be more "Real tests" (the "examples" will be removed)
!!! News tests will be in "realtests" !!!

python3.7 -m pytest REALTESTS
python3 -m pytest --cov-report html --cov=reqman REALTESTS/   --> 75% cov currently
python3 -m pytest --cov-report html --cov=reqman tests/ REALTESTS/   --> 95% cov currently
