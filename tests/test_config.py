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

    with pytest.raises(ValueError):
        pop_config()

    with pytest.raises(ValueError):
        push_config()
        pop_config()
        pop_config()

    with tempfile.TemporaryDirectory() as tdir:
        with cfiddle_config(Executable_type=MyExecutable, CFIDDLE_BUILD_ROOT=tdir):
            assert isinstance(build_one("test_src/test.cpp"), MyExecutable)

        with pytest.raises(ValueError):
            pop_config()

        assert not isinstance(build_one("test_src/test.cpp"), MyExecutable)
        

class MyExecutable(Executable):
        pass

