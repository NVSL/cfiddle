from cfiddle import *
from fixtures import *
from cfiddle.Builder import Builder, ExecutableDescription, Executable, InvalidBuildParameter
from cfiddle.config import get_config, cfiddle_config
from cfiddle.Toolchain import GCCToolchain
import os
import pytest

class NopBuilder(Builder):
    def build(self):
        return self.result_factory(lib=f"{self.source_file}.so",
                                   build_dir=self.build_directory,
                                   toolchain=GCCToolchain("C", {}),
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


def test_default_parameters(setup):
    with cfiddle_config(build_parameters_default=arg_map(OPTIMIZE="-O1")):
        b = build("test_src/test.cpp")
        assert b[0].build_spec.build_parameters == dict(OPTIMIZE="-O1")

        b = build("test_src/test.cpp", build_parameters=arg_map(OPTIMIZE="-O3"))
        assert b[0].build_spec.build_parameters == dict(OPTIMIZE="-O3")

def test_default_parameters2(setup):
    with cfiddle_config(build_parameters_default= arg_map(MORE_INCLUDES="-DFOO", DEBUG_FLAGS="-DBAR")):
        histo = build(code(""), build_parameters=arg_map(OPTIMIZE="-O3 -fopenmp"))
        print(histo[0].get_build_parameters())

def test_builder_construction(test_cpp_nop_builder, setup):

    assert test_cpp_nop_builder.source_file == "test_src/test.cpp"
    assert test_cpp_nop_builder.source_name_base == "test"
    assert test_cpp_nop_builder.build_parameters == dict(OPTIMIZE="-O1")
    assert test_cpp_nop_builder.build_root == os.path.join(get_config("CFIDDLE_BUILD_ROOT"),"build")
    assert test_cpp_nop_builder.build_directory.startswith(test_cpp_nop_builder.build_root)



def test_nop_build(test_cpp_nop_builder, setup):

    result = test_cpp_nop_builder.build()
    
    assert isinstance(result, Executable)
    

def test_alt_build_directory(setup):
    t = NopBuilder(build_spec = ExecutableDescription(source=code(""), build_parameters={}), build_root="/tmp")
    assert t.build_root == "/tmp"


def test_equal_in_build_parameters(setup):
    t = build("test_src/test.cpp", build_parameters=arg_map(OPTIMIZE="-march=skylake"), verbose=True, rebuild=True)
    run(t, function="four")

def test_long_build_parameters(setup):
    t = build("test_src/test.cpp", build_parameters=arg_map(OPTIMIZE="-O3 -fno-semantic-interposition -funroll-all-loops -finline -march=native -finline-limit=2000 -funsafe-loop-optimizations -fgcse-after-reload -fgcse-las -fgcse-sm -fpeel-loops  -fgcse-after-reload -fgcse-las -fgcse-sm -fpeel-loops"))
    run(t,  function="four")

    
def test_slash_in_build_parameters(setup):
    t = build("test_src/test.cpp", build_parameters=arg_map(FOO="a/b/bc/"))
    run(t,  function="four")

    
def test_mixins(setup):
    class MyResult(Executable):
        def my_result(self):
            return "my_result"
        
    t = NopBuilder(build_spec = ExecutableDescription(source=code(""), build_parameters={}), result_factory=MyResult)
    result = t.build()
    assert isinstance(result, MyResult)
    assert result.my_result() == "my_result"

def _test_numeric_parameters(setup):
    build(1, arg_map(OPTIMIZE=1))
    
def test_invalid_parameters(setup):
    with cfiddle_config():
        enable_debug()
        with pytest.raises(CFiddleException):
            build(1, arg_map(OPTIMIZE=None))

        with pytest.raises(InvalidBuildParameter):
            build("test_src/test.cpp", arg_map(OPTIMIZE=None))

        with pytest.raises(InvalidBuildParameter):
            build("test_src/test.cpp", arg_map(OPTIMIZE=True))

        with pytest.raises(InvalidBuildParameter):
            build("test_src/test.cpp", arg_map(OPTIMIZE={}))

        with pytest.raises(InvalidBuildParameter):
            build("test_src/test.cpp", [{4:""}])

        with pytest.raises(InvalidBuildParameter):
            build("test_src/test.cpp", build_parameters={"boo":"bar"})
            
def test_rebuild(setup):
    n = code(r"""
extern "C"
int number() {
    return 4;
}
""", file_name="number.cpp")

    b = build("number.cpp")
    assert run(b, "number")[0].return_value == 4
    n = code(r"""
extern "C"
int number() {
    return 5;
}
""", file_name="number.cpp")
    assert run(b.rebuild(), "number")[0].return_value == 5
    
