from fiddle import *
from fiddle.Builder import Executable
import fiddle

def test_configuration():

    assert isinstance(build_one("test_src/test.cpp"), Executable)

    class MyExecutable(Executable):
        pass

    old = fiddle.get_config("Executable_type")
    fiddle.set_config("Executable_type", MyExecutable)
    assert isinstance(build_one("test_src/test.cpp"), MyExecutable)
    fiddle.set_config("Executable_type", old)
    
