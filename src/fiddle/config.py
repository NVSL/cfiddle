from .Data import InvocationResultsList
from .Builder import Executable, ExecutableDescription
from .MakeBuilder import MakeBuilder
from .Runner import InvocationResult, InvocationDescription
from .LocalRunner import LocalRunner
from .CProtoParser import CProtoParser
from .source import FullyInstrumentedExecutable

fiddle_config = dict(Executable_type=FullyInstrumentedExecutable,
                     InvocationResult_type=InvocationResult,
                     Builder_type=MakeBuilder,
                     Runner_type=LocalRunner,
                     InvocationResultsList_type=InvocationResultsList,
                     ExecutableDescription_type=ExecutableDescription,
                     InvocationDescription_type=InvocationDescription,
                     ProtoParse_type=CProtoParser)



def set_config(k,v):
    fiddle_config[k] = v

def get_config(k):
    return fiddle_config[k]
    
