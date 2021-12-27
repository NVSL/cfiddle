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
    "code",
    "build_and_run",
    "build",
    "run",
    "configure_for_jupyter",
    "sanity_test",
    "UnknownSymbol",
    "changes_in"
]

from .Data import InvocationResultsList
from .Builder import ExecutableDescription, Executable
from .MakeBuilder import MakeBuilder
from .Runner import InvocationDescription, InvocationResult
from .LocalRunner import LocalRunner, UnknownSymbol
from .util import map_product, changes_in
from .Code import code
from .config import get_config, set_config
from .jupyter import configure_for_jupyter

def build_and_run(source_file, build_parameters, function, arguments):
    executable = build_one(source_file, build_parameters)

    return run_one(executable, function, arguments)


def build(source, build_parameters=None, **kwargs):

    if build_parameters is None:
       build_parameters = {}

    if isinstance(build_parameters, dict):
        build_parameters = [build_parameters]

    Builder = get_config("Builder_type")
    ExeDesc = get_config("ExecutableDescription_type")
    return [Builder(ExeDesc(source, build_parameters=p), **kwargs).build() for p in build_parameters]


def run(invocations, **kwargs):
    IRList = get_config("InvocationResultsList_type")
    Runner = get_config("Runner_type")
    InvDesc = get_config("InvocationDescription_type")
    return IRList(Runner(InvDesc(**i), **kwargs).run() for i in invocations)


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
    return run([dict(executable=build(code('extern "C" int foo() {return 4;}'))[0],
                     function="foo",
                     arguments={})])[0].return_value

PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')

setup_ld_path()

