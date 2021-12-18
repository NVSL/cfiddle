from .Runner import Runner, InvocationResult
import ctypes
import tempfile
import os
from .util import environment
import csv


class LocalRunner(Runner):

    def __init__(self, build_result, runnable, result_factory=None):
        super().__init__(build_result, runnable, result_factory=result_factory)
        self._libfiddle = ctypes.CDLL("libfiddle.so")
        
    def run(self):
        self._reset_data_collection()
        self._invoke_function()
        results = self._collect_data()
        return self._result_factory(runnable=self._runnable, results=results)
    
    def _invoke_function(self):
        self._arguments = self.bind_arguments(self._runnable.arguments, self._build_result.functions[self._runnable.function])
        
        c_lib = ctypes.CDLL(self._build_result.lib)
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
        _, source_file_name = os.path.split(self._build_result.source_file)
        result_file_name = f"{source_file_name}.{self._runnable.function}({arg_string}).csv"
        return os.path.join(self._build_result.build_dir, result_file_name)

#run = LocalRunner()

