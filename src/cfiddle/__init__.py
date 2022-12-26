__all__ = [
    "InvocationResultsList",
    "ExecutableDescription",
    "Executable",
    "MakeBuilder",
    "InvocationDescription",
    "Invoker",
    "Runner",
    "DirectRunner",
    "arg_map",
    "arg_product",
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
    "cfiddle_config",
    "get_config"
]

from .Data import InvocationResultsList
from .Builder import ExecutableDescription, Executable, ExecutableList
from .MakeBuilder import MakeBuilder, InvalidBuildParameter
from .Runner import InvocationDescription, InvocationResult, Runner, InvalidRunOption, DirectRunner
from .Invoker import Invoker
from .util import arg_map, arg_product, changes_in, exp_range, running_under_jupyter, ArgProductError
from .Code import code
from .config import get_config, set_config, enable_debug, cfiddle_config
from .paths import setup_ld_path
from .perfcount import are_perf_counters_available
from .Toolchain import list_architectures
from .Exceptions import CFiddleException, handle_cfiddle_exceptions


def build_and_run(source_file=None, build_parameters=None, function=None, arguments=None, run_options=None, perf_counters=None):
    executable = build(source_file, build_parameters)
    return run(executable, function, arguments, run_options, perf_counters)

def build_list(build_specs, **kwargs):
    Builder = get_config("Builder_type")
    ExeDesc = get_config("ExecutableDescription_type")
    progress_bar = get_config("ProgressBar")

    l = ExecutableList()
    for p in progress_bar(build_specs, miniters=1):
        l.append(Builder(ExeDesc(**p), **kwargs).build())
    return l

@handle_cfiddle_exceptions
def build(source, build_parameters=None, **kwargs):
    """Compile one or more source files in one or more ways.

    ``source`` can be a single file name  or a list of file names.  ``build``
    compiles each file into an :obj:`Executable`.  A call to
    :func:`cfiddle.code()` is often passed as ``source``.

    ``build_parameters`` can set parameters for the build process
    (e.g., optimization levels, the target architecture, or the
    compiler to use).  It can be a :obj:`dict` or list of :obj:`dict`
    that provide values for build parameters.  If ``build_parameters``
    is ``None``, defaults will be used.

    Typically, the :code:`build_parameters` value is generated with
    :func:`cfiddle.util.arg_map()`.

    ``build`` compiles each source file using each set of build parameters, and
    returns list of resulting :obj:`InstrumentedExecutable` objects.

    The :obj:`InstrumentedExecutable` s can be studied themselves or passed to :func:`run`.

    Args:
        source: One or more (as a list) of source files to compile.
        build_parameters:  One or more (as a list) :obj:`dict` listing build parameters.  Defaults to None.
        **kwargs:  Further options to the :obj:`Builder` object that perform compilation.

    Returns:
        list of :obj:`Executable`: One executable for each combination of ``source`` and ``build_parameters``.

    """

    if build_parameters is None:
        build_parameters = arg_map()

    default_build_parameters = get_config("build_parameters_default")
    if default_build_parameters is None:
        default_build_parameters = arg_map()

    try:
        full_build_parameters = arg_product(default_build_parameters, build_parameters)
    except ArgProductError as e:
        raise InvalidBuildParameter(e)
        

    builds = arg_map(source=source, build_parameters=full_build_parameters)
    return build_list(builds, **kwargs)


def run_list(invocations, **kwargs):

    IRList = get_config("InvocationResultsList_type")
    IRType = get_config("InvocationResult_type")
    Runner = get_config("Runner_type")
    Invoker = get_config("Invoker_type")
    InvDesc = get_config("InvocationDescription_type")
    progress_bar = get_config("ProgressBar")

    return Runner([InvDesc(**i) for i in invocations],
                  invoker=Invoker,
                  result_list_factory=IRList,
                  result_factory=IRType,
                  progress_bar=progress_bar,
                  **kwargs).run()


@handle_cfiddle_exceptions
def run(executable, function, arguments=None, perf_counters=None, run_options=None, **kwargs):
    """Run one or more functions with one or more sets of arguments and
    collect one or more measurements.
    
    CFiddle parameterizes execution in five ways, corresponding to
    :func:`run()` 's five arguments:
    
    1. An :obj:`InstrumentedExecutable` to run as returned by :func:`cfiddle.build()`.
    2. The function to call.
    3. The arguments to pass to the function.
    4. The performance counters to track.
    5. And the other aspects of the execution environment (e.g., environment variables and clock speed).

    :func:`run()` can take multiple values for each of these and will
    run all combinations.  

    :code:`function` can be a :obj:`str` corresponding to a function
    that is present in each executable with the same signature.  To
    run multiple functions, pass a list of strings.

    The contents of :code:'arguments` must match the signature of the
    function invoked.  While you can pass a :code:`dict` (for a single
    invocation) or list of :code:`dict` (to invoke the function
    multiple times), it's easiest to just always invoke
    :func:`cfiddle.arg_map()` to generate this argument.

    :code:`perf_counters` should be a list of :doc:`performance
    counter <./perfcount>` names or a list of such lists.  If it is a
    list of lists, it will result in multiple invocations using
    different sets of counters.

    You can set default values for :code:`perf_counters` by setting
    the :code:`perf_counters_default` configuration value.  Passing a
    value to :func:`run()` completely overrides the default.

    By default, :code:`run_options` interpreted by
    :obj:`cfiddle.Runner.RunOptionInterpreter`.  The default
    implementation copies the contents of `run_options` to environment
    variables before execution.

    You can set default values for :code:`run_options` by setting the
    :code:`run_options_default` configuration value.  You set it to
    the result of a call to :func:`cfiddle.arg_map()`.  The values you
    pass to :func:`run()` will override the defaults.  If the defaults
    includes multiple sets of values, :func:`run()` will run all
    combinations of the defaults and the values passed supplied.

    :code:`run()` returns an :obj:`cfiddle.InvocationResultsList` which is a
    subclass of :obj:`list` that can format results in useful ways
    (e.g., as a Panda dataframe or CSV file).

    The elements of the list are :obj:`cfiddle.InvocationResult` objects.
    Each of which contains the build parameter for the executable used
    and all the parameters listed aabove.

    Args:
       executable: An :obj:`Executable` or list of :obj:`Executable` objects.
       function: A ``str`` or list of ``str`` naming functions to call.
       arguments: A :obj:`dict` of arguments for the function.  Or a list of such :obj:`dict`.  Defaults to ``[{}]``
       perf_counters: A list of performance counters to collect. Default to None.
       run_options: Parameters controlling how the function is run.  Default to None.

    Returns:
       :obj:`InvocationResultsList`:  A list of :obj:`InvocationResult` objects.

    """
    
    if arguments is None:
        arguments = arg_map()
        
    if run_options is None:
        run_options = arg_map()

    default_run_options = get_config("run_options_default")
    if default_run_options is None:
        default_run_options = arg_map()

    if perf_counters is None:
        perf_counters = get_config("perf_counters_default")
        if perf_counters is None:
            perf_counters = []

    try:
        full_run_options = arg_product(default_run_options, run_options)
    except ArgProductError as e:
        raise InvalidRunOption(e)
    

    perf_counters = normalize_perf_counters(perf_counters)
    
    invocations = arg_map(executable=executable, function=function, arguments=arguments, run_options=full_run_options, perf_counters=perf_counters)
    return run_list(invocations, **kwargs)


def normalize_perf_counters(perf_counters):
    # this allows for us to say run(foo, "bar", arg_map(), perf_counters=["cycles", "instructions"] and
    # not have arg_map generate on invocation for "cycles" and one for 'instructions'
    # the alternative seems to be to require [["cycles", "instructions"]], which is ugly.
    if perf_counters is None:
        return None
    if not isinstance(perf_counters, str) and all(isinstance(pc, str) for pc in perf_counters):
        return [perf_counters]
    else:
        return perf_counters
    
def sanity_test():
    return run(executable=build(code('extern "C" int foo() {return 4;}')),
               function=["foo"])[0].return_value


if running_under_jupyter():
    # do this hear so we don't suck in jupyter unless we actually need it.
    from .jupyter import configure_for_jupyter
    configure_for_jupyter()
    
setup_ld_path()

