import os
import pkg_resources

from .Builder import BuildSpec
from .MakeBuilder import MakeBuilder
from .LocalRunner import LocalRunner
from .Runner import Invocation, Runnable
from .Data import InvocationResultsList


def build_and_run(source_file, build_parameters, function, arguments):
    build = BuildSpec(source_file, build_parameters=build_parameters)

    invocations_spec = Runnable(function=function, arguments=arguments)
    
    executable = MakeBuilder(build, verbose=True).build()

    invocation = Invocation(executable, invocations_spec)

    result = LocalRunner(invocation).run()
    return result

def setup_ld_path():
    PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')
    ld_paths = os.environ["LD_LIBRARY_PATH"].split(":");
    ld_paths += os.path.join(PACKAGE_DATA_PATH, "libfiddle")
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
