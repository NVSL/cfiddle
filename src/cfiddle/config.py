import copy

from .Data import InvocationResultsList
from .Builder import Executable, ExecutableDescription
from .MakeBuilder import MakeBuilder
from .Runner import InvocationResult, InvocationDescription
from .LocalRunner import LocalRunner
from .CProtoParser import CProtoParser
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
                      ProtoParse_type=CProtoParser,
                      CFIDDLE_BUILD_ROOT=".cfiddle/builds",
                      ProgressBar=noop_progress_bar)


cfiddle_config_stack = []
cfiddle_config_stack.append(default_config)

    
def set_config(k,v):
    global cfiddle_config_stack
    cfiddle_config_stack[-1][k] = v

    
def get_config(k):
    # TODO several places check the environment first and then look here. We sohuld factor that out.
    global cfiddle_config_stack
    return cfiddle_config_stack[-1][k]


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
        raise ValueError("Poping the cfiddle configuration stack would leave it empty.")
    cfiddle_config_stack = cfiddle_config_stack[:-1]
