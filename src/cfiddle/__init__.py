__all__ = [
    "InvocationResultsList",
    "ExecutableDescription",
    "Executable",
    "MakeBuilder",
    "InvocationDescription",
    "LocalRunner",
    "arg_map",
    "code",
    "build_and_run",
    "build",
    "run",
    "run_list",
    "sanity_test",
    "changes_in",
    "exp_range",
    "are_perf_counters_available",
    "list_architectures",
    "CFiddleException",
    "enable_debug",
    "enable_interactive",
    "cfiddle_config"
]

from .Data import InvocationResultsList
from .Builder import ExecutableDescription, Executable
from .MakeBuilder import MakeBuilder
from .Runner import InvocationDescription, InvocationResult
from .LocalRunner import LocalRunner
from .util import arg_map, changes_in, exp_range, running_under_jupyter
from .Code import code
from .config import get_config, set_config, enable_debug, enable_interactive, cfiddle_config
from .paths import setup_ld_path
from .perfcount import are_perf_counters_available
from .Toolchain import list_architectures
from .Exceptions import CFiddleException, handle_cfiddle_exceptions

def build_and_run(source_file, build_parameters, function, arguments):
    executable = build_one(source_file, build_parameters)

    return run_one(executable, function, arguments)

@handle_cfiddle_exceptions
def build(source, build_parameters=None, **kwargs):
    """Compile one or more source files using one or more different ways.

    ``source`` can be a single filename or a list of file names.  ``build``
    compiles each file into an :obj:`Executable`.  A call to :func:`code()` is
    often passed as ``source``.

    ``build_parameters`` can set parameters for the build process (e.g.,
    optimization levels or the compiler to use).  It can be a :obj:`dict` or list
    of :obj:`dict` that provide values for build parameters.  If
    ``build_parameters`` is ``None``, defaults will be used.

    Typically, the :code:`build_parameters` value is generated with :func:`cfiddle.util.arg_map()`.

    ``build`` compiles each source file using each set of build parameters, and
    returns list of resulting :obj:`Executable` objects.

    The :obj:`Executable` s can be studied themselves or passed to :func:`run`.

    Args:
        source: One or more (as a list) of source files to compile.
        build_parameters:  One or more (as a list) :obj:`dict` listing build parameters.  Defaults to None.
        **kwargs:  Further options to the :obj:`Builder` object that perform compilation.

    Returns:
        list of :obj:`Executable`: One executable for each combination of ``source`` and ``build_parameters``.

    """

    if build_parameters is None:
       build_parameters = [{}]

    builds = arg_map(source=source, build_parameters=build_parameters)
    
    Builder = get_config("Builder_type")
    ExeDesc = get_config("ExecutableDescription_type")
    progress_bar = get_config("ProgressBar")

    l = []
    for p in progress_bar(builds, miniters=1):
        l.append(Builder(ExeDesc(**p), **kwargs).build())
    return l


def run_list(invocations, perf_counters=None, **kwargs):
    if perf_counters is None:
        perf_counters = []

    IRList = get_config("InvocationResultsList_type")
    Runner = get_config("Runner_type")
    InvDesc = get_config("InvocationDescription_type")
    progress_bar = get_config("ProgressBar")
    
    l = IRList()
    for i in progress_bar(invocations, miniters=1):
        l.append(Runner(InvDesc(**i, perf_counters=perf_counters), **kwargs).run())
    return l

@handle_cfiddle_exceptions
def run(executable, function, arguments=None, perf_counters=None, **kwargs):
    """Run one or more functions with one or more sets of arguments.

    Run each ``function`` in each :obj:`Executable` using each set of arguments,
    and collect the data provided by each ``perf_counter`` for each invocation.

    Each ``function`` must exist in each :obj:`Executable` and they must have the
    same signature.  Further, each set of arguments must match the function
    signature (i.e., the key-value pairs in ``arguments`` must align with names
    and types of the function's arguments).

    The value of ``arguments`` is typically provided by a call to
    :func:`cfiddle.util.arg_map()`.

    Returns an :obj:`InvocationResultsList` which is a subclass of :obj:`list`
    that can format results in useful ways (e.g., as a Panda dataframe or CSV
    file).

    The elements of the list are :obj:`InvocationResult` objects.  Each of
    which contains the parameters and results for each invocation.

    Args:
       executable: An :obj:`Executable` or list of :obj:`Executable` objects.
       function: A ``str`` or list of ``str`` naming functions to call.
       arguments: A :obj:`dict` of arguments for the function.  Or a list of such :obj:`dict`.  Defaults to ``{}``
       perf_counters: A list of performance counters to collect. Default to None.

    Returns:
       :obj:`InvocationResultsList`:  A list of :obj:`InvocationResult` objects.

    """
    
    if arguments is None:
        arguments = [{}]

    invocations = arg_map(executable=executable, function=function, arguments=arguments)
    return run_list(invocations, perf_counters=perf_counters, **kwargs)
        

def sanity_test():
    return run(executable=build(code('extern "C" int foo() {return 4;}')),
               function=["foo"])[0].return_value


if running_under_jupyter():
    # do this hear so we don't suck in jupyter unless we actually need it.
    from .jupyter import configure_for_jupyter
    configure_for_jupyter()
    
setup_ld_path()

