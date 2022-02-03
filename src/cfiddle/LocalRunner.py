from .Runner import Runner, InvocationResult, RunnerException
from .Exceptions import CFiddleException
import ctypes
import tempfile
import os
from .util import environment
from .perfcount import install_perf_counters, clear_perf_counters
import csv
import faulthandler

faulthandler.enable()

class LocalRunner(Runner):

    def __init__(self, invocation, result_factory=None):
        super().__init__(invocation, result_factory=result_factory)
        self._libcfiddle = ctypes.CDLL("libcfiddle.so")
        
    def run(self):
        self._reset_data_collection()
        return_value = self._invoke_function()
        results = self._collect_data()
        return self._result_factory(invocation=self.get_invocation(), results=results, return_value=return_value)
    
    def _invoke_function(self):
        
        self.bound_arguments = self.bind_arguments(self.get_invocation().arguments, self._get_function(self.get_invocation().function))
        
        f = self._load_symbol()
        return f(*self.bound_arguments)

    def _load_symbol(self):
        try:
            c_lib = ctypes.CDLL(self.get_build_result().lib)
            return getattr(c_lib, self.get_invocation().function)
        except AttributeError:
            raise RunnerException(f"Couldn't find '{self.get_invocation().function}' in '{self.get_build_result().lib}'.  Do you need to recompile? or declare it `extern \"C\"`?.")
        
    def _get_function(self, f):
        try:
            return self.get_build_result().functions[f]
        except KeyError:
            raise RunnerException(f"Couldn't find Prototype for '{f}'.  Options are [{' '.join(self.get_build_result().functions.keys())}].  Did you declare it 'extern \"C\"'?.")
        
    def _reset_data_collection(self):
        clear_perf_counters()
        install_perf_counters(self._invocation.perf_counters)
        self._libcfiddle.clear_stats()

    def _collect_data(self):
        output_file = self._build_results_path()
        
        self._write_results(output_file)

        return self._read_results(output_file)

    
    def _read_results(self, output_file):
        with open(output_file) as infile:
            return [r for r in csv.DictReader(infile)]

        
    def _write_results(self, filename):
        self._libcfiddle.write_stats(ctypes.c_char_p(filename.encode()))

    
    def _build_results_path(self):
        arg_string = ", ".join(map(lambda x: str(x.value), self.bound_arguments))
        _, source_file_name = os.path.split(self.get_build_result().build_spec.source_file)
        result_file_name = f"{source_file_name}.{self.get_invocation().function}({arg_string}).csv"
        return os.path.join(self.get_build_result().build_dir, result_file_name)
    
    
