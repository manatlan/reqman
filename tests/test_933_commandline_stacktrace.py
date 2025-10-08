import pytest
import reqman
import os

def test_stacktrace_on_error_in_debug_mode_jules(monkeypatch, capsys):
    """ Test that a stacktrace is printed to stderr on error when in debug mode """
    # Set sys.argv to run reqman with the --d flag and an invalid option
    monkeypatch.setattr("sys.argv", ["reqman", "--d", "--invalid-option"])

    # Run the main function, which should catch the RMCommandException and print the stack trace
    reqman.main()

    # Capture the stderr output
    captured = capsys.readouterr()

    # Assert that the traceback is in the stderr output
    assert "Traceback (most recent call last):" in captured.err
    assert "RMCommandException: bad option" in captured.err