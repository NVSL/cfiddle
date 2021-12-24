import os
import pkg_resources

__all__ = [
    "InvocationResultsList",
    "ExecutableDescription",
    "Executable",
    "MakeBuilder",
    "InvocationDescription",
    "LocalRunner",
    "map_product",
    "product",
    "code",
    "build_and_run",
    "build",
    "build_one",
    "run",
    "run_one",
    "configure_for_jupyter",
    "sanity_test"
]

from itertools import product
from .Data import InvocationResultsList
from .Builder import ExecutableDescription, Executable
from .MakeBuilder import MakeBuilder
from .Runner import InvocationDescription, InvocationResult
from .LocalRunner import LocalRunner
from .util import map_product
from .Code import code
from .config import get_config, set_config
from .jupyter import configure_for_jupyter
    
def build_and_run(source_file, build_parameters, function, arguments):
    executable = build_one(source_file, build_parameters)

    return run_one(executable, function, arguments)


def build(source, parameters=None, **kwargs):

    if parameters is None:
       parameters = {}

    if isinstance(parameters, dict):
        parameters = [parameters]

    Builder = get_config("Builder_type")
    ExeDesc = get_config("ExecutableDescription_type")
    return [Builder(ExeDesc(source, build_parameters=p), **kwargs).build() for p in parameters]


def build_one(*args, **kwargs):
    r = build(*args, **kwargs)
    if len(r) != 1:
        ValueError("You specified more than one build.")
    return r[0]


def run(invocations, **kwargs):
    IRList = get_config("InvocationResultsList_type")
    Runner = get_config("Runner_type")
    InvDesc = get_config("InvocationDescription_type")
    return IRList(Runner(InvDesc(*i), **kwargs).run() for i in invocations)


def run_one(exe, function, arguments=None, **kwargs):
    if arguments is None:
        arguments = {}
    return run([(exe, function, arguments)], **kwargs)[0]

def libfiddle_dir_path():
    PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')    
    return os.path.join(PACKAGE_DATA_PATH, "libfiddle")

def print_libfiddle_dir():
    print(libfiddle_dir_path())

def setup_ld_path():

    if "LD_LIBRARY_PATH" in os.environ:
        ld_paths = os.environ["LD_LIBRARY_PATH"].split(":")
    else:
        ld_paths = []
    ld_paths.append(libfiddle_dir_path())
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
    return os.environ["LD_LIBRARY_PATH"]

def set_ld_path_in_shell():
    print(f"export LD_LIBRARY_PATH={setup_ld_path()}")
    
def sanity_test():
    return run_one(build_one(code('extern "C" int foo() {return 4;}')), "foo").return_value

PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

setup_ld_path()

