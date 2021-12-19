import os
import pkg_resources

__all__ = [
    "InvocationResultsList",
    "ExecutableDescription",
    "Executable",
    "MakeBuilder",
    "InvocationDescription",
    "LocalRunner",
    "expand_args",
    "code",
    "build_and_run",
    "build",
    "build_one",
    "run"
]


from .Data import InvocationResultsList
from .Builder import ExecutableDescription, Executable
from .MakeBuilder import MakeBuilder
from .Runner import InvocationDescription
from .LocalRunner import LocalRunner
from .util import expand_args
from .Code import code

def build_and_run(source_file, build_parameters, function, arguments):
    executable = build_one(source_file, build_parameters)

    return run(executable, function, arguments)


def build(source, parameters=None, **kwargs):

    if parameters is None:
       parameters = {}

    if isinstance(parameters, dict):
        parameters = [parameters]

    return [MakeBuilder(ExecutableDescription(source, build_parameters=p), **kwargs).build() for p in parameters]

def build_one(*args, **kwargs):
    r = build(*args, **kwargs)
    if len(r) != 1:
        ValueError("You specified more than one build.")
    return r[0]


def run(exe=None, function=None, arguments=None,
        invocations=None,
        **kwargs):
    
    if exe is not None:
        if invocations is not None:
            raise ValueError("You can only specify 'invocations' or 'exe', 'function', and 'arguments'")
        if  function is None:
            raise ValueError("You must specify 'function' with 'exe'")
        if arguments is None:
            arguments = {}
        invocations = [(exe, function, arguments)]
        
    return InvocationResultsList(LocalRunner(InvocationDescription(*i), **kwargs).run() for i in invocations)



def setup_ld_path():
    PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')
    ld_paths = os.environ["LD_LIBRARY_PATH"].split(":");
    ld_paths += os.path.join(PACKAGE_DATA_PATH, "libfiddle")
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
