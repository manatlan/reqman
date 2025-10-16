import reqman
import pytest
from reqman import common
import sys

def test_decode_bytes_utf8_jules():
    """Tests decoding of a UTF-8 byte string."""
    assert common.decodeBytes("hello".encode('utf-8')) == "hello"

def test_decode_bytes_cp1252_jules():
    """Tests decoding of a cp1252 byte string."""
    assert common.decodeBytes("hello".encode('cp1252')) == "hello"

def test_decode_bytes_latin1_fallback_jules():
    """Tests the latin-1 fallback for undecodable byte strings."""
    # This byte sequence is invalid in both UTF-8 and cp1252
    invalid_bytes = b'\x81\x8d\x8f\x90\x9d'
    assert common.decodeBytes(invalid_bytes) == invalid_bytes.decode('latin-1')

def test_prettify_json_jules():
    """Tests that prettify correctly formats a JSON string."""
    json_string = '{"a": 1, "b": 2}'
    pretty_json = '{\n    "a": 1,\n    "b": 2\n}'
    assert reqman.prettify(json_string) == pretty_json

def test_prettify_xml_jules():
    """Tests that prettify correctly formats an XML string."""
    xml_string = "<root><child>data</child></root>"
    pretty_xml = '<?xml version="1.0" ?>\n<root>\n    <child>data</child>\n</root>'
    assert reqman.prettify(xml_string) == pretty_xml

def test_prettify_unsupported_chars_windows_jules(monkeypatch):
    """
    Tests that prettify handles unsupported characters on Windows
    by backslash-escaping them.
    """
    if sys.platform != 'win32':
        pytest.skip("This test is for Windows only")

    # Simulate a Windows environment with a cp1252 console encoding
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setattr(sys.stdout, 'encoding', 'cp1252')

    text_with_unsupported_char = "hello \u0100 world"
    # The \u0100 character is not supported in cp1252
    expected_output = "hello \\u0100 world"
    assert reqman.prettify(text_with_unsupported_char) == expected_output