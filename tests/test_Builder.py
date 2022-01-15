from cfiddle import *
from fixtures import *
from cfiddle.Builder import Builder, ExecutableDescription, Executable
from cfiddle.config import get_config
import os
import pytest

class NopBuilder(Builder):
    def build(self):
        return self.result_factory(lib=f"{self.source_file}.so",
                                   build_dir=self.build_directory,
                                   output="no output",
                                   build_command="build something",
                                   build_spec=self.build_spec, 
                                   functions=dict())
    

def test_create_spec(setup):
    build_spec = ExecutableDescription(source="test_src/test.cpp",
                                       build_parameters=dict(OPTIMIZE="-O1"))

    
@pytest.fixture
def test_cpp_nop_builder(setup):
    return NopBuilder(build_spec = ExecutableDescription(source="test_src/test.cpp",
                                                         build_parameters=dict(OPTIMIZE="-O1")))


def test_builder_construction(test_cpp_nop_builder, setup):

    assert test_cpp_nop_builder.source_file == "test_src/test.cpp"
    assert test_cpp_nop_builder.source_name_base == "test"
    assert test_cpp_nop_builder.build_parameters == dict(OPTIMIZE="-O1")
    assert test_cpp_nop_builder.build_root == os.path.join(get_config("CFIDDLE_BUILD_ROOT"),"build")
    assert test_cpp_nop_builder.build_directory.startswith(test_cpp_nop_builder.build_root)
    assert "OPTIMIZE" in test_cpp_nop_builder.build_directory 
    assert "O1" in test_cpp_nop_builder.build_directory


def test_nop_build(test_cpp_nop_builder, setup):

    result = test_cpp_nop_builder.build()
    
    assert isinstance(result, Executable)
    

def test_alt_build_directory(setup):
    t = NopBuilder(build_spec = ExecutableDescription(source="", build_parameters={}), build_root="/tmp")
    assert t.build_root == "/tmp"
    

def test_mixins(setup):
    class MyResult(Executable):
        def my_result(self):
            return "my_result"
        
    t = NopBuilder(build_spec = ExecutableDescription(source="", build_parameters={}), result_factory=MyResult)
    result = t.build()
    assert isinstance(result, MyResult)
    assert result.my_result() == "my_result"

    
def test_invalid_parameters(setup):
    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=None))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=True))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=[]))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE={}))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", {4:""})

        
    
