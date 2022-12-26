import ctypes
import tempfile
import os
import csv
import faulthandler

from .Runner import Runner, InvocationResult, RunnerException, RunOptionInterpreter
from .CProtoParser import funcptr_t
from .Exceptions import CFiddleException
from .util import environment
from .perfcount import install_perf_counters, clear_perf_counters


faulthandler.enable()

class Invoker:

    def __init__(self, invocation, result_factory=None):
        from .config import get_config
        self._libcfiddle = ctypes.CDLL("libcfiddle.so")
        self._invocation = invocation
        self._result_factory = result_factory or get_config("InvocationResult_type")
        self._run_option_manager = get_config("RunOptionInterpreter_type")
        
    def run(self):
        self._prepare_data_collection()

        return_value = self._invoke_function()
        results = self._collect_data()
        return self._result_factory(invocation=self._invocation, results=results, return_value=return_value)

    def _get_build_result(self):
        return self._invocation.executable

    def _resolve_function_pointer_arguments(self):
        def resolve(b):
            if isinstance(b, funcptr_t):
                r = self._load_symbol(b.function_name)
                r.value = b.function_name # this is ugly.
                return r
            else:
                return b
        
        self.bound_arguments = [resolve(b) for b in self.bound_arguments]
        
    def _invoke_function(self):
        self.bound_arguments = Runner.bind_arguments(self._invocation.arguments, self._get_function(self._invocation.function))
        self._resolve_function_pointer_arguments()
        
        f = self._load_symbol(self._invocation.function)
        
        with self._run_option_manager(self._invocation.run_options):
            return f(*self.bound_arguments)
    
    def _load_symbol(self, symbol):
        try:
            c_lib = ctypes.CDLL(self._get_build_result().lib)
            #t = getattr(c_lib, self._invocation.function)
            return getattr(c_lib, symbol)
        except AttributeError:
            raise RunnerException(f"Couldn't find '{symbol}' in '{self._get_build_result().lib}'.  Do you need to recompile? or declare it `extern \"C\"`?.")
        
    def _get_function(self, f):
        try:
            return self._get_build_result().functions[f]
        except KeyError:
            raise RunnerException(f"Couldn't find Prototype for '{f}'.  Options are [{' '.join(self._get_build_result().functions.keys())}].  Did you declare it 'extern \"C\"'?.")
        
    def _prepare_data_collection(self):
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
        _, source_file_name = os.path.split(self._get_build_result().build_spec.source_file)
        result_file_name = f"{source_file_name}.{self._invocation.function}({arg_string}).csv"
        return os.path.join(self._get_build_result().build_dir, result_file_name)
    
    
