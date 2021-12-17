from .Builder import Builder, BuildResult, BadBuildParameter, BuildFailure
import os
import subprocess
import pytest
from shutil import copyfile
from .util import environment, invoke_process

import pkg_resources


DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

class MakeBuilder(Builder):

    def __init__(self,
                 rebuild=False,
                 makefile=None):
        super().__init__()

        self._makefile = makefile
        if self._makefile is None:
            self._makefile = os.path.join(DATA_PATH, "make", "fiddle.make")

        self._rebuild = rebuild
        self._verbose = False
        
        
    def build_one(self, parameters=None):
        build_directory = self._compute_build_directory(parameters)

        so_make_target = self._compute_so_make_target(build_directory)
        so_unique_name = self._compute_so_unique_name(build_directory)

        vpath = ":".join([os.path.dirname(self._source_file), build_directory])

        parameter_strings  = [f"{name}={value}" for name, value in parameters.items()]
        parameter_strings += [f"BUILD={build_directory}"]
        parameter_strings += [f"FIDDLE_INCLUDE={os.path.join(DATA_PATH, 'include')}"]
        parameter_strings += [f"FIDDLE_VPATH={vpath}"]
        
        base_cmd = ["make", "-f", self._makefile] + parameter_strings
        
        if self._rebuild:
            make_targets = ["clean"]
        else:
            make_targets = []
            
        make_targets.append(so_make_target)

        if self._verbose:
            print(base_cmd + make_targets)
        output = self._invoke_make(base_cmd + make_targets)
        if self._verbose:
            print(output)

        copyfile(so_make_target, so_unique_name)

        functions = self.parser.parse_file(self._source_file)
            
        return BuildResult(lib=so_unique_name,
                           source_file=self._source_file,
                           functions=functions,
                           build_command=self._build_manual_make_cmd(base_cmd + make_targets),
                           build_dir=build_directory,
                           output=output,
                           parameters=parameters)


    def rebuild(self, rebuild=True):
        self._rebuild = rebuild

        
    def makefile(self, makefile):
        self._makefile = makefile

        
    def verbose(self, verbose=True):
        self._verbose = verbose

        
    def _build_manual_make_cmd(self, cmd):
        return " ".join(cmd)

    
    def _invoke_make(self, cmd):
        success, output = invoke_process(cmd)
        if not success:
            raise BuildFailure(" ".join(cmd), output)
        return output

    
    def _compute_so_make_target(self, build_directory):
        return os.path.join(build_directory, f"{self._source_name_base}.so")

    
    def _compute_so_unique_name(self, build_directory):
        number = 0

        while True:
            unique_path = os.path.join(build_directory, f"{self._source_name_base}_{number}.so")
            if not os.path.exists(unique_path):
                break
            number += 1

        return unique_path


build = MakeBuilder()

import ctypes

@pytest.fixture
def make_builder_build():
    build = MakeBuilder()
    build.rebuild(True)
    build.verbose(True)
    return build


def test_simple(make_builder_build):
    simple_test = make_builder_build("test_src/test.cpp")
    assert os.path.exists(simple_test.lib)
    assert len(simple_test.functions) == 5
    assert ctypes.CDLL(simple_test.lib).nop() == 4

    
def test_cxx(make_builder_build):
    simple_test_cxx = make_builder_build("test_src/test_cxx.cxx")
    assert os.path.exists(simple_test_cxx.lib)
    assert len(simple_test_cxx.functions) == 1
    assert ctypes.CDLL(simple_test_cxx.lib).nop() == 5

    
def test_c(make_builder_build):
    simple_test_c = make_builder_build("test_src/test_c.c")
    assert os.path.exists(simple_test_c.lib)
    assert len(simple_test_c.functions) == 1
    assert ctypes.CDLL(simple_test_c.lib).nop() == 6

    
def test_alt_makefile(make_builder_build):
    make_builder_build.makefile("test_src/test.make")
    make_builder_build.rebuild(True)
    alternate_result = make_builder_build("test_src/test.cpp")
    with open(alternate_result.lib) as lib:
        assert lib.read() == "test_src/test.cpp\n"

    
def test_complex_flags(make_builder_build):
    simple_test = make_builder_build("test_src/test.cpp", OPTIMIZE="-O1 -fno-inline")
    assert os.path.exists(simple_test.lib)


    
