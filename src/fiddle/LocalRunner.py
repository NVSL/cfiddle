from .Runner import Runner, InvocationResult
import ctypes
import tempfile
import os
from .util import environment
import csv


class LocalRunner(Runner):

    def __init__(self, invocation, result_factory=None):
        super().__init__(invocation, result_factory=result_factory)
        self._libfiddle = ctypes.CDLL("libfiddle.so")
        
    def run(self):
        self._reset_data_collection()
        self._invoke_function()
        results = self._collect_data()
        return self._result_factory(invocation=self.get_invocation(), results=results)
    
    def _invoke_function(self):
        
        self.bound_arguments = self.bind_arguments(self.get_invocation().arguments, self.get_build_result().functions[self.get_invocation().function])
        
        c_lib = ctypes.CDLL(self.get_build_result().lib)
        f = getattr(c_lib, self.get_invocation().function)
        f(*self.bound_arguments)

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
        arg_string = ", ".join(map(lambda x: str(x.value), self.bound_arguments))
        _, source_file_name = os.path.split(self.get_build_result().source_file)
        result_file_name = f"{source_file_name}.{self.get_invocation().function}({arg_string}).csv"
        return os.path.join(self.get_build_result().build_dir, result_file_name)

#run = LocalRunner()

