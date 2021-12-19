from fiddle.MakeBuilder import MakeBuilder
from fiddle.Builder import ExecutableDescription, Executable
import os
import pytest
import ctypes


@pytest.fixture
def test_cpp_builder():
    return MakeBuilder(build_spec = ExecutableDescription(source_file="test_src/test.cpp",
                                              build_parameters=dict(OPTIMIZE="-O1")))


@pytest.mark.parametrize("source,function_count,return_value",[
    ("test_src/test.cpp", 8, 4),
    ("test_src/test_cxx.cxx", 1,5),
    ("test_src/test_c.c", 1,6)])
def test_build(source, function_count, return_value):
    simple_test = MakeBuilder(build_spec=ExecutableDescription(source, build_parameters={}), verbose=True, rebuild=True)
    result = simple_test.build()
    assert os.path.exists(result.lib)
    assert len(result.functions) == function_count
    assert ctypes.CDLL(result.lib).nop() == return_value

    

def test_alt_makefile():
    builder = MakeBuilder(ExecutableDescription(source_file="test_src/test.cpp", build_parameters={}),
                          makefile="test_src/test.make",
                          rebuild=True,
                          verbose=True)
    alternate_result = builder.build()
    with open(alternate_result.lib) as lib:
        assert lib.read() == "test_src/test.cpp\n"

    
def test_complex_flags():
    builder = MakeBuilder(ExecutableDescription(source_file="test_src/test.cpp", build_parameters=dict(OPTIMIZE="-O1 -fno-inline")))
    result = builder.build()
    assert os.path.exists(result.lib)

