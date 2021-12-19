from fiddle.Builder import Builder, ExecutableDescription, Executable
import pytest

class NopBuilder(Builder):
    def build(self):
        return self.result_factory(f"{self.source_file}.so", self.source_file, self.build_directory, "no output", str(self.build_parameters), self.build_parameters, {f"{self.source_name_base}_func": "nonsense_value"})
    

def test_create_spec():
    build_spec = ExecutableDescription(source_file="test_src/test.cpp",
                                       build_parameters=dict(OPTIMIZE="-O1"))

    
@pytest.fixture
def test_cpp_nop_builder():
    return NopBuilder(build_spec = ExecutableDescription(source_file="test_src/test.cpp",
                                                         build_parameters=dict(OPTIMIZE="-O1")))


def test_builder_construction(test_cpp_nop_builder):

    assert test_cpp_nop_builder.source_file == "test_src/test.cpp"
    assert test_cpp_nop_builder.source_name_base == "test"
    assert test_cpp_nop_builder.build_parameters == dict(OPTIMIZE="-O1")
    assert test_cpp_nop_builder.build_root == "fiddle/builds"
    assert test_cpp_nop_builder.build_directory.startswith("fiddle/builds")
    assert "OPTIMIZE" in test_cpp_nop_builder.build_directory 
    assert "O1" in test_cpp_nop_builder.build_directory

    
def test_nop_build(test_cpp_nop_builder):

    result = test_cpp_nop_builder.build()
    
    assert isinstance(result, Executable)
    

def test_alt_build_directory():
    t = NopBuilder(build_spec = ExecutableDescription(source_file="", build_parameters={}), build_root="/tmp")
    assert t.build_root == "/tmp"
    

def test_mixins():
    class MyResult(Executable):
        def my_result(self):
            return "my_result"
        
    t = NopBuilder(build_spec = ExecutableDescription(source_file="", build_parameters={}), result_factory=MyResult)
    result = t.build()
    assert isinstance(result, MyResult)
    assert result.my_result() == "my_result"
    
