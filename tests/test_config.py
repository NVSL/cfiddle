from fiddle import *
from util import *
from fiddle.Builder import Executable
from fiddle.config import *
import fiddle
import pytest

def test_configuration():

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
    
    with fiddle_config(Executable_type=MyExecutable):
        assert isinstance(build_one("test_src/test.cpp"), MyExecutable)

    with pytest.raises(ValueError):
        pop_config()

    assert not isinstance(build_one("test_src/test.cpp"), MyExecutable)
        

class MyExecutable(Executable):
        pass

