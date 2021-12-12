from .Builder import Builder, BuildResult, BadBuildParameter, BuildFailure
import os
import subprocess
import pytest

from .util import environment, invoke_process

import pkg_resources

DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

class MakeBuilder(Builder):

    def __init__(self,
                 rebuild=False,
                 build_root=None,
                 makefile=None):
        super().__init__()

        self.build_root = build_root
        if self.build_root is None:
            self.build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")

        self._makefile = makefile
        if self._makefile is None:
            self._makefile = os.path.join(DATA_PATH, "make", "fiddle.make")

        self._rebuild=rebuild

    def rebuild(self, rebuild=True):
        self._rebuild = rebuild
        return self

    def makefile(self, makefile):
        self._makefile = makefile
        return self
        
    def _compute_build_directory(self, source_file, parameters):
        _, source_name = os.path.split(source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return os.path.join(self.build_root, "__".join([f"{p}_{v}" for p,v in parameters.items()])+source_name_base)

    def _compute_so_name(self, source_file, build_directory):
        _, source_name = os.path.split(source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return os.path.join(build_directory, f"{source_name_base}.so")

    def build_one(self, source_file, parameters=None):
        build_directory = self._compute_build_directory(source_file, parameters)
        
        parameter_strings  = [f"{name}={value}" for name, value in parameters.items()]
        parameter_strings += [f"BUILD={build_directory}"]
        parameter_strings += [f"FIDDLE_INCLUDE={os.path.join(DATA_PATH, 'include')}"]
        vpath = ":".join([os.path.dirname(source_file), build_directory])
        parameter_strings += [f"FIDDLE_VPATH={vpath}"]
        
        base_cmd = ["make", "-f", self._makefile] + parameter_strings
        
        if self._rebuild:
            cmd=base_cmd + ["clean"]
            print(" ".join(cmd))
            success, output = invoke_process(cmd)
            if not success:
                raise BuildFailure(" ".join(cmd), output)

        so_name = self._compute_so_name(source_file, build_directory)

        cmd = base_cmd + [so_name]
        print(" ".join(cmd))
        success, output = invoke_process(cmd)
        if not success:
            raise BuildFailure(" ".join(cmd), output)

        functions = self.parser.parse_file(source_file)
            
        return BuildResult(lib=so_name, functions=functions, build_command=" ".join(cmd), build_dir=build_directory, output=output, parameters=parameters)

build = MakeBuilder()

def test_make_builder():
    import ctypes
    import tempfile
    from .util import expand_args
    builder = MakeBuilder()

    build.rebuild(True)
    simple_test = build("test_src/test.cpp")
    assert os.path.exists(simple_test.lib)
    assert len(simple_test.functions) == 4;
    assert ctypes.CDLL(simple_test.lib).nop() == 4
    
    alternate_makefile_build = MakeBuilder()
    alternate_makefile_build.makefile("test_src/test.make")
    alternate_makefile_build.rebuild(True)
    alternate_result = alternate_makefile_build("test_src/test.cpp")
    with open(alternate_result.lib) as lib:
        assert lib.read() == "test_src/test.cpp\n"

    with tempfile.TemporaryDirectory() as build_root:
        alternate_root_build = MakeBuilder(build_root=build_root, rebuild=True)
        alt_root_simple_test =  alternate_root_build("test_src/test.cpp")
        assert os.path.exists(alt_root_simple_test.lib)
        assert len(alt_root_simple_test.functions) == 4;
        assert ctypes.CDLL(alt_root_simple_test.lib).nop() == 4
    
    with pytest.raises(BuildFailure):
        build("test_src/broken.cpp")
    build("test_src/broken.cpp", MORE_CXXFLAGS="-DDONT_BREAK")
    
