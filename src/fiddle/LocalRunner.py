from .Runner import Runner, Result, do_run
import ctypes
import tempfile
import os
from .Parameters import bind_parameters
from .util import environment
import csv

class LocalRunner(Runner):

    def run_one(self, r, output_root=None):

        if output_root is None:
            output_root = os.environ.get("FIDDLE_OUTPUT_ROOT", "fiddle/runs")

        args = bind_parameters(r.arguments, r.build.functions[r.function])

        d, f = os.path.split(r.build.lib)
        arg_string = ", ".join(map(lambda x: str(x.value), args))
        output_directory = os.path.join(output_root, f"{f}.{r.function}({arg_string})")

        os.makedirs(output_directory, exist_ok=True)

        c_lib = ctypes.CDLL(r.build.lib)

        with environment(FIDDLE_OUTPUT_DIR=output_directory):
            f = getattr(c_lib, r.function)
            f(*args)

        return Result(output_directory=output_directory, runnable=r)
    

def run(*argc, **kwargs):
    return do_run(LocalRunner(), *argc, **kwargs)
