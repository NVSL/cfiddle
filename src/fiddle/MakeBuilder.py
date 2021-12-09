from .Builder import Builder, BuildResult, BadBuildParameter, BuildFailure, do_build
import os
import subprocess
import pytest
from .util import environment

import pkg_resources

DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

class MakeBuilder(Builder):

    def build_one(self, source_file, parameters=None, build_directory=None, build_root=None, makefile=None, rebuild=False):
        if build_root is None:
            build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")
        if makefile is None:
            makefile = os.path.join(DATA_PATH, "make", "fiddle.make")
        if build_directory is None:
            build_directory = os.path.join(build_root, "__".join([f"{p}_{v}" for p,v in parameters.items()]))
        if "=" in build_directory:
            raise BadBuildParameter(f"'{build_directory}' is not a valid build directory.")

        
        functions = self.parser.parse_file(source_file)
        
        parameter_strings=[f"{name}={value}" for name, value in parameters.items()]
        parameter_strings += [f"BUILD={build_directory}"]
        
        source_directory, source_name = os.path.split(source_file)
        source_name_base, source_name_ext = os.path.splitext(source_name)

        target = f"{source_name_base}.so"

        so_name = os.path.join(build_directory, target)

        target = os.path.join(build_directory, )

        base_cmd = ["make", "-f", makefile] + parameter_strings

        with environment(FIDDLE_INCLUDE=os.path.join(DATA_PATH, "include")):
            if rebuild:
                try:
                    cmd=base_cmd + ["clean"]
                    print(" ".join(cmd))
                    p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                    output = p.stdout
                except subprocess.CalledProcessError as e:
                    raise BuildFailure(e.output.decode() + "\n"+" ".join(cmd))

            try:
                cmd = base_cmd + [so_name]
                print(" ".join(cmd))
                p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                output = p.stdout
            except subprocess.CalledProcessError as e:
                    raise BuildFailure(e.output.decode() + "\n"+" ".join(cmd))

        return BuildResult(lib=so_name, functions=functions, build_command=" ".join(cmd), build_dir=build_directory, output=output,parameters=parameters)

def build(*argc, **kwargs):
    return do_build(MakeBuilder(), *argc, **kwargs)

    
def test_make_builder():
    from .util import cross_product
    builder = MakeBuilder()
    r = builder.build("test.cpp", build_directory="test", rebuild=True)
    print(r.output.decode())
    r = builder.build("test.cpp", build_directory="test", parameters=[{}], rebuild=True)
    print(r[0].output.decode())
    
    r = builder.build("test_src/test.cpp", build_directory="test_src_build", parameters=dict(MORE_SRC="test2.cc"), rebuild=True)
    print(r.output.decode())
    with pytest.raises(BuildFailure) as r:
        builder.build("broken.cpp", build_directory="broken", rebuild=True)
    print(r.value.args[0].output.decode())
    
    r = builder.build("broken.cpp", parameters=dict(MORE_CFLAGS="-DDONT_BREAK"), rebuild=True)
    print(r.output.decode())
    r = [builder.build("broken.cpp", parameters=p, rebuild=True) for p in cross_product([("MORE_CFLAGS",["-DDONT_BREAK"])])]
    print(r[0].output.decode())
    
    with pytest.raises(BuildFailure) as r:
        [builder.build("broken.cpp", parameters=p, rebuild=True) for p in cross_product([("MORE_CFLAGS",["-DDONT_BREAK", ""])])]
    print(r.value.args[0].output.decode())



    
