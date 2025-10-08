import pytest
import reqman
import logging

def test_COMMAND_debug_flag_jules(monkeypatch, caplog):
    """ test the --d command line argument """
    monkeypatch.setattr("sys.argv", ["reqman", "--d", "tests/test_002_prettify.py"])
    with caplog.at_level(logging.DEBUG):
        reqman.main()
    assert "DEBUG" in caplog.text