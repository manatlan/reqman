import pytest, reqman, json
import datetime,pickle


def test_Env_dyn():
    env=reqman.Env( {"a":42} )
    assert env == {"a":42}

    env2=env.clone()
    assert env2 == {"a":42}

    env2.save("yolo",13)

    assert env2["yolo"] == 13
    assert "yolo" not in env

