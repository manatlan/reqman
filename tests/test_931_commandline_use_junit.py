import reqman,pytest,sys,os

def test_COMMAND_output_junit_xml(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: http://localhost:8080/
          tests:
            - status: 200
        """)
    assert not os.path.isfile("reqman.html")

    x=exe(".","--j")

    assert os.path.isfile("reqman.html")
    assert os.path.isfile("reqman.xml")

    with open("reqman.xml","r+") as fid:
        buf=fid.read()
        assert "testsuites>" in buf
        assert "testsuite>" in buf
        assert "testcase>" in buf

def test_COMMAND_output_junit_xml_named(exe):
    with open("f.yml","w+") as fid:
        fid.write("""
        - GET: http://localhost:8080/
        """)
    assert not os.path.isfile("reqman.html")

    x=exe(".","--j:junit.xml")

    assert os.path.isfile("reqman.html")
    assert not os.path.isfile("reqman.xml")
    assert os.path.isfile("junit.xml")

    with open("junit.xml","r+") as fid:
        buf=fid.read()
        assert "testsuites>" in buf
        assert "testsuite>" in buf
        assert "testcase>" in buf
