import os
import pkg_resources

from .Builder import ExecutableDescription
from .MakeBuilder import MakeBuilder
from .LocalRunner import LocalRunner
from .Runner import InvocationDescription
from .Data import InvocationResultsList


def build_and_run(source_file, build_parameters, function, arguments):
    executable = build(source_file, build_parameters)

    invocation = InvocationDescription(executable, function=function, arguments=arguments)

    return LocalRunner(invocation).run()

def build(source_file, build_parameters):

    build = ExecutableDescription(source_file, build_parameters=build_parameters)

    return MakeBuilder(build, verbose=True).build()


def setup_ld_path():
    PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')
    ld_paths = os.environ["LD_LIBRARY_PATH"].split(":");
    ld_paths += os.path.join(PACKAGE_DATA_PATH, "libfiddle")
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
