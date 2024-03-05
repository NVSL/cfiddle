from cfiddle import *
from util import *
from cfiddle.Builder import Executable
from cfiddle.config import *
from fixtures import *
import cfiddle
import pytest

def test_configuration(setup):

    assert isinstance(build_one("test_src/test.cpp"), Executable)

    push_config()
    set_config("Executable_type", MyExecutable)
    assert isinstance(build_one("test_src/test.cpp"), MyExecutable)
    pop_config()
    assert not isinstance(build_one("test_src/test.cpp"), MyExecutable)


def test_push_pop():

    with pytest.raises(IllegalConfiguration):
        pop_config()

    with pytest.raises(IllegalConfiguration):
        push_config()
        pop_config()
        pop_config()

def test_push_pop2():

    with tempfile.TemporaryDirectory() as tdir:
        with cfiddle_config(Executable_type=MyExecutable, CFIDDLE_BUILD_ROOT=tdir):
            assert isinstance(build("test_src/test.cpp")[0], MyExecutable)

        assert not isinstance(build("test_src/test.cpp")[0], MyExecutable)
        

def test_peek():
    with tempfile.TemporaryDirectory() as tdir:
        with cfiddle_config(Executable_type=MyExecutable, CFIDDLE_BUILD_ROOT=tdir):
            peek_config() # shouldn't change anything.
            assert isinstance(build("test_src/test.cpp")[0], MyExecutable)
        

def test_unknown_option():
    with pytest.raises(IllegalConfiguration):
        with cfiddle_config(foo="bar"):
            pass

def test_force():
    with cfiddle_config():
        set_config("foo", "bar", force=True)
        assert get_config("foo") == "bar"
        with cfiddle_config(baz="boom", force=True):
            assert get_config("baz") == "boom"

def test_default():
    with cfiddle_config():
        assert get_config("foo", "bar") == "bar"
        
class MyExecutable(Executable):
        pass

