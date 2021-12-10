from .Builder import Builder, BuildResult, BadBuildParameter, BuildFailure
import os
import subprocess
import pytest
import warnings

from .util import environment

import pkg_resources

DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

class MakeBuilder(Builder):

    def build_one(self, source_file, parameters=None, build_directory=None, build_root=None, makefile=None, rebuild=False):
        if isinstance(source_file, str):
            source_file = [source_file]
        if build_root is None:
            build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")
        if makefile is None:
            makefile = os.path.join(DATA_PATH, "make", "fiddle.make")
        if build_directory is None:
            build_directory = os.path.join(build_root, "__".join([f"{p}_{v}" for p,v in parameters.items()])+source_file[0])
        if "=" in build_directory:
            raise BadBuildParameter(f"'{build_directory}' is not a valid build directory.")

        source_directories = [os.path.dirname(x) for x in source_file]
        if len(set(source_directories)) != 1:
            warnings.warn(f"Source files in different directories is not reliable: {' '.join(source_file)}")

        vpath = ":".join(source_directories + [build_directory])

        functions = {}
        for s in source_file:
            functions.update(self.parser.parse_file(s))
            
        parameter_strings=[f"{name}={value}" for name, value in parameters.items()]
        parameter_strings += [f"BUILD={build_directory}"]
        parameter_strings += [f"FIDDLE_VPATH={vpath}"]
        parameter_strings += [f"FIDDLE_INCLUDE={os.path.join(DATA_PATH, 'include')}"]
        
        base_cmd = ["make", "-f", makefile] + parameter_strings
        
        if rebuild:
            try:
                cmd=base_cmd + ["clean"]
                print(" ".join(cmd))
                p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                output = p.stdout
            except subprocess.CalledProcessError as e:
                raise BuildFailure(" ".join(cmd), e.output.decode())
            
        try:
            _, source_name = os.path.split(source_file[0])
            source_name_base, _ = os.path.splitext(source_name)
            so_name = os.path.join(build_directory, f"{source_name_base}.so")
            
            cmd = base_cmd + [so_name]
            print(" ".join(cmd))
            p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            output = p.stdout
        except subprocess.CalledProcessError as e:
            raise BuildFailure(" ".join(cmd), e.output.decode())

        return BuildResult(lib=so_name, functions=functions, build_command=" ".join(cmd), build_dir=build_directory, output=output,parameters=parameters)

build  = MakeBuilder()

#def build(*argc, **kwargs):
#    return do_build(MakeBuilder(), *argc, **kwargs)

    
def test_make_builder():
    from .util import expand_args
    builder = MakeBuilder()


    r = build("test_src/test.cpp", build_directory="test", parameters=[{}], rebuild=True)
    assert isinstance(r, list), "If a list of parameters is passed, return a list"


    r = build("test_src/test.cpp", build_directory="test", rebuild=True)
    assert not isinstance(r, list), "If 0 or 1 sets of parameters are passed, return a singleton"

    r = build("test_src/test.cpp", build_directory="test", parameters={}, rebuild=True)
    assert not isinstance(r, list), "If 0 or 1 sets of parameters are passed, return a singleton"
    
    r = builder.build("test_src/test.cpp", build_directory="test", rebuild=True)
    print(r.output.decode())
    r = builder.build("test_src/test.cpp", build_directory="test", parameters=[{}], rebuild=True)
    assert isinstance(r, list)
    print(r[0].output.decode())
    
    r = builder.build("test_src/test.cpp", build_directory="test_src_build", parameters=dict(MORE_SRC="test_src/test2.cc"), rebuild=True)
    print(r.output.decode())
    with pytest.raises(BuildFailure) as r:
        builder.build("test_src/broken.cpp", build_directory="broken", rebuild=True)
    print(r.value.args)
    
    r = builder.build("test_src/broken.cpp", parameters=dict(MORE_CFLAGS="-DDONT_BREAK"), rebuild=True)
    print(r.output.decode())
    r = [builder.build("test_src/broken.cpp", parameters=p, rebuild=True) for p in expand_args(MORE_CFLAGS=["-DDONT_BREAK"])]
    print(r[0].output.decode())
    
    with pytest.raises(BuildFailure) as r:
        [builder.build("test_src/broken.cpp", parameters=p, rebuild=True) for p in expand_args(MORE_CFLAGS=["-DDONT_BREAK", ""])]
    print(r.value.args)

    
def test_analysis():
    def get_functions(result):
        return list(result.functions.keys())
    build.register_analysis(get_functions)
    assert build("test_src/std_maps.cpp").get_functions() == ["ordered", "unordered"];
    
