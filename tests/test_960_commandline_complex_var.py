import reqman, pytest, sys, os


def test_COMMAND_complex(exe):
    mock = {"/hello": (200, "ok")}

    with open("f.yml", "w+") as fid:
        fid.write(
            """
        - GET: /<<var.a.b>>
          tests:
            - status: 200
            - content: ok
          params:
            var: |
                d={}
                d["a"]={"b":"hello"}
                return d
        """
        )

    x = exe(".", fakeServer=mock)
    # x.view()
    assert x.rc == 0


def test_COMMAND_complex2(exe):
    mock = {"/HELLO": (200, "ok")}

    with open("f.yml", "w+") as fid:
        fid.write(
            """
        - GET: /<<var.a.b|upper>>
          tests:
            - status: 200
            - content: ok
          params:
            var: |
                d={}
                d["a"]={"b":"hello"}
                return d
            upper:
              return x.upper()
        """
        )

    x = exe(".", fakeServer=mock)
    assert x.rc == 0


def test_priority_token(
    exe
):  # current major reqman's tests !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # PROBABLY THE MOST IMPORTANT TEST ;-)
    # (BASE FEATURE FROM DAY ONE)

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
          token: fake

          BEGIN:
            - GET: /token 
              save: token
        """
        )

    f = """
      - GET: /<<token>>
        tests:
          status: 200
      - GET: /<<token>>
        params:
          token: real2  #override temporaly
        tests:
          status: 201
      - GET: /<<token>>
        tests:
          status: 200
    """
    with open("f1.yml", "w+") as fid:
        fid.write(f)
    with open("f2.yml", "w+") as fid:
        fid.write(f)

    MOCK = {"/token": (200, "real"), "/real": (200, "ok"), "/real2": (201, "ok")}
    x = exe(".", fakeServer=MOCK)
    # x.view()
    assert x.rc == 0


def test_env_hermetic_between_files(exe):  # pato trouble
    MOCK = {"/first": (200, "second"), "/second": (200, "ok")}

    with open("f1.yml", "w+") as fid:
        fid.write(
            """
        - GET: /first
          save: data
        - GET: /<<data>>
          tests:
            - status: 200
        """
        )

    with open("f2.yml", "w+") as fid:
        fid.write(
            """
        - GET: /<<data>>
          tests:
            - status: 404
        """
        )

    x = exe(".", fakeServer=MOCK)
    # x.view()
    assert x.rc == 1  # 1 error coz the 404 test is non playable


def test_ensure_global_proc_doesnt_save_globally(exe):
    MOCK = {"/first": (200, "second"), "/second": (200, "ok")}

    with open("reqman.conf", "w+") as fid:
        fid.write(
            """
          GLOBAL:
            - GET: /first
              save: data
        """
        )

    with open("f1.yml", "w+") as fid:
        fid.write(
            """
        - call: GLOBAL
        - GET: /<<data>>
          tests:
            - status: 200
        """
        )

    with open("f2.yml", "w+") as fid:
        fid.write(
            """
        - GET: /<<data>>
          tests:
            - status: 404
        """
        )

    x = exe(".", fakeServer=MOCK)
    # x.view()
    assert x.rc == 1  # 1 error coz the 404 test is non playable
