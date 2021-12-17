from .Runner import Runner, InvocationResult
import ctypes
import tempfile
import os
from .util import environment
import csv


class LocalRunner(Runner):

    def run_one(self, runnable):
        
        args = self.bind_arguments(runnable.arguments, runnable.build.functions[runnable.function])

        d, f = os.path.split(runnable.build.lib)
        arg_string = ", ".join(map(lambda x: str(x.value), args))
        output_root=runnable.build.build_dir
        output_directory = os.path.join(output_root, f"{f}.{runnable.function}({arg_string})")

        os.makedirs(output_directory, exist_ok=True)

        c_lib = ctypes.CDLL(runnable.build.lib)

        with environment(FIDDLE_OUTPUT_DIR=output_directory):
            f = getattr(c_lib, runnable.function)
            f(*args)
            
        return InvocationResult(output_directory=output_directory, runnable=runnable)

run = LocalRunner()


def test_hello_world():
    from fiddle.MakeBuilder import build
    b = build("test_src/hello.cpp", code=r"""
    #include<cstdio>

    extern "C"
    int foo(int i) {
        fprintf(stdout, "hello world!\n");
        return 0;
    }
    """, OPTIMIZE=["-O0", "-O3"])

    run(build=b, function=["foo"], arguments=[dict(i=1)])
    b = build("test_src/hello.cpp", code=r"""
    #include<cstdio>

    extern "C"
    int foo(int i) {
        fprintf(stdout, "goodbye world!\n");
        return 0;
    }
    """, OPTIMIZE=["-O0", "-O3"])

    run(build=b, function=["foo"], arguments=[dict(i=1)])
