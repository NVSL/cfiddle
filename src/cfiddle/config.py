import copy

from .Data import InvocationResultsList
from .Builder import Executable, ExecutableDescription
from .MakeBuilder import MakeBuilder
from .Runner import InvocationResult, InvocationDescription
from .LocalRunner import LocalRunner
from .CProtoParser import CProtoParser
from .GoProtoParser import GoProtoParser
from .Exceptions import CFiddleException
from .source import FullyInstrumentedExecutable
from tqdm import tqdm
from contextlib import contextmanager

def noop_progress_bar(data, *argc, **kwargs):
    return data

default_config = dict(Executable_type=FullyInstrumentedExecutable,
                      InvocationResult_type=InvocationResult,
                      Builder_type=MakeBuilder,
                      Runner_type=LocalRunner,
                      InvocationResultsList_type=InvocationResultsList,
                      ExecutableDescription_type=ExecutableDescription,
                      InvocationDescription_type=InvocationDescription,
                      ProtoParser_types=[CProtoParser, GoProtoParser],
                      CFIDDLE_BUILD_ROOT=".cfiddle/builds",
                      ProgressBar=noop_progress_bar,
                      DEBUG_MODE=False,
                      DONT_RAISE=False)


cfiddle_config_stack = []
cfiddle_config_stack.append(default_config)

    
def set_config(k,v):
    global cfiddle_config_stack
    cfiddle_config_stack[-1][k] = v

    
def get_config(k):
    # TODO several places check the environment first and then look here. We sohuld factor that out.
    global cfiddle_config_stack
    return cfiddle_config_stack[-1][k]

def enable_debug(v=True):
    set_config("DEBUG_MODE", v)

def in_debug():
    return get_config("DEBUG_MODE")

def enable_interactive(v=True):
    set_config("DONT_RAISE", v)
    

@contextmanager
def cfiddle_config(**kwargs):
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
        raise IllegalConfiguration("Poping the cfiddle configuration stack would leave it empty.")
    cfiddle_config_stack = cfiddle_config_stack[:-1]

class IllegalConfiguration(CFiddleException):
    pass
