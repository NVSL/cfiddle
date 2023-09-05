import functools
import delegate_function
from cfiddle.SelfContainedExecutionMethod import SelfContainedExecutionMethod

def execution_method(config):
    return functools.partial(SelfContainedExecutionMethod, delegate_function.DelegateGenerator(yaml=config))
