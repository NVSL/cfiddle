from .Runner import Runner, InvocationResult
import ctypes
import tempfile
import os
from .util import environment
import csv


class LocalRunner(Runner):

    def run_one(self, runnable):
        return LocalInvocation(self, runnable).run()
    
class LocalInvocation:

    def __init__(self, runner, runnable):
        self._runner = runner
        self._runnable = runnable
        self._arguments = None
        self._libfiddle = ctypes.CDLL("libfiddle.so")
        
    def run(self):
        self._reset_data_collection()
        self._invoke_function()
        results = self._collect_data()
        return InvocationResult(runnable=self._runnable, results=results)

    
    def _invoke_function(self):
        self._arguments = self._runner.bind_arguments(self._runnable.arguments, self._runnable.build.functions[self._runnable.function])
        
        c_lib = ctypes.CDLL(self._runnable.build.lib)
        f = getattr(c_lib, self._runnable.function)
        f(*self._arguments)

    
    def _reset_data_collection(self):
        self._libfiddle.clear_stats()


    def _collect_data(self):
        output_file = self._build_results_path()
        
        self._write_results(output_file)

        return self._read_results(output_file)

    
    def _read_results(self, output_file):
        with open(output_file) as infile:
            return [r for r in csv.DictReader(infile)]

        
    def _write_results(self, filename):
        self._libfiddle.write_stats(ctypes.c_char_p(filename.encode()))

    
    def _build_results_path(self):
        arg_string = ", ".join(map(lambda x: str(x.value), self._arguments))
        _, source_file_name = os.path.split(self._runnable.build.source_file)
        result_file_name = f"{source_file_name}.{self._runnable.function}({arg_string}).csv"
        return os.path.join(self._runnable.build.build_dir, result_file_name)

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
