import copy
from tqdm import tqdm
from contextlib import contextmanager

from .Data import InvocationResultsList
from .Builder import Executable, ExecutableDescription
from .MakeBuilder import MakeBuilder
from .Runner import InvocationResult, InvocationDescription, Runner, RunOptionInterpreter, SubprocessDelegate
from .Invoker import Invoker
from .CProtoParser import CProtoParser
from .GoProtoParser import GoProtoParser
from .Exceptions import CFiddleException
from .source import InstrumentedExecutable


def noop_progress_bar(data, *argc, **kwargs):
    return data

default_config = dict(Executable_type=InstrumentedExecutable,
                      InvocationResult_type=InvocationResult,
                      Builder_type=MakeBuilder,
                      Runner_type=Runner,
                      Invoker_type=Invoker,
                      InvocationResultsList_type=InvocationResultsList,
                      ExecutableDescription_type=ExecutableDescription,
                      InvocationDescription_type=InvocationDescription,
                      ProtoParser_types=[CProtoParser, GoProtoParser],
                      CFIDDLE_BUILD_ROOT=".cfiddle/builds",
                      ProgressBar=noop_progress_bar,
                      RunnerDelegate_type=SubprocessDelegate,
                      RunOptionInterpreter_type=RunOptionInterpreter,
                      perf_counters_default=None,
                      build_parameters_default=None,
                      run_options_default=None,
                      DEBUG_MODE=False)


cfiddle_config_stack = []
cfiddle_config_stack.append(default_config)

    
def set_config(k,v):
    """Set a configuration values.

    Args:
      k:  The name of the configuration variable.
      v:  The value.
    """

    global cfiddle_config_stack
    cfiddle_config_stack[-1][k] = v

    
def get_config(k):
    """Query a configuration values.

    Args:
      k:  The name of the configuration variable.

    Returns:
      The value in the current configuration.
    """

    # TODO several places check the environment first and then look here. We sohuld factor that out.
    global cfiddle_config_stack
    return cfiddle_config_stack[-1][k]

def enable_debug(enable=True):
    """Put CFiddle into debugging mode.

    Args:
      enable:  New value for the internal debug mode flag.  :code:`True` mean debug is enabled.  Defaults to :code:`True`.
    """
    set_config("DEBUG_MODE", enable)

def in_debug():
    return get_config("DEBUG_MODE")


@contextmanager
def cfiddle_config(**kwargs):
    """Create a local configuration context.

    Any configuration changes made inside this context will be undone after the context completes.

    For example:
    
.. doctest ::

    >>> from cfiddle import *
    >>> get_config("DEBUG_MODE")
    False
    >>> with cfiddle_config():
    ...    enable_debug()
    ...    print(get_config("DEBUG_MODE"))
    True
    >>> print(get_config("DEBUG_MODE"))
    False

    """

    push_config()
    [set_config(k,v) for k,v in kwargs.items()]
    try:
        yield
    finally:
        pop_config()
        

def push_config():
    global cfiddle_config_stack
    cfiddle_config_stack.append(copy.deepcopy(cfiddle_config_stack[-1]))

    
def pop_config():
    global cfiddle_config_stack
    if len(cfiddle_config_stack) == 1:
        raise IllegalConfiguration("Popping the cfiddle configuration stack would leave it empty.")
    cfiddle_config_stack = cfiddle_config_stack[:-1]

def peek_config():
    global cfiddle_config_stack
    return copy.deepcopy(cfiddle_config_stack[-1])

class IllegalConfiguration(CFiddleException):
    pass


