import pytest
import copy
import os
from contextlib import contextmanager
from collections.abc import Iterable
import subprocess
from itertools import product


def map_product(**parameters):
    """
    Generate a set of parameter assignments from a dict or parameter names and values.

    map_product(dict(a=range(1,3),
                b=1)

    yields:

    [{"a": 1, "b": 1},  {"a": 2, "b": 1}])

    """
    def listify(t):
        return t if isinstance(t, Iterable) and not isinstance(t, str) else [t]
    t = [(k, listify(v)) for k,v in parameters.items()]
    return _cross_product(t)


def _cross_product(parameters):
    if len(parameters) == 0:
        return []
    if len(parameters) == 1:
        name, values = parameters[0]
        return [{name:v} for v in values]
    
    ret = []
    rest = _cross_product(parameters[:-1])
    name, values = parameters[-1]
    for r in rest:
        for v in values:
            t = copy.copy(r)
            t[name] = v
            ret.append(t)
            
    return ret


def invoke_process(cmd):
    try:
        p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        return True, p.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()

    
class ListDelegator(list):
    
    def __getattr__(self, requested_attribute):     
        if self.is_callable_by_all(requested_attribute):
            return self.create_list_invoker(requested_attribute)
        elif self.is_attr_of_all(requested_attribute):
            return self.create_list_of_values(requested_attribute)
        else:
            raise ValueError(f"{requested_attribute} is not available for all items")

        
    def map(self, f, *argc, **kwargs):
        return ListDelegator([f(x, *argc, **kwargs) for x in self])

    
    def is_callable_by_all(self, attribute):
        return all([callable(getattr(x, attribute)) for x in self])

            
    def is_attr_of_all(self, attribute):
        return all([hasattr(x, attribute) for x in self])

            
    def create_list_invoker(self, requested_method):
        def create_list_of_results(*argc, **kwargs):
            return ListDelegator([getattr(i, requested_method)(*argc, **kwargs) for i in self])
        return create_list_of_results

            
    def create_list_of_values(self, requested_attr):
        return ListDelegator([getattr(i, requested_attr) for i in self])


@contextmanager
def working_directory(path):
    here = os.getcwd()
    try:
        log.debug(f"changing to {path}")
        os.chdir(path)
        log.debug(f"in {os.getcwd()}")
        yield path
    finally:
        os.chdir(here)

@contextmanager
def environment(**kwds):
    env = copy.deepcopy(os.environ)
    for k,v in kwds.items():
        if v is None:
            del os.environ[k]
        else:
            os.environ[k] = v

    try:
        yield None
    finally:
        os.environ.clear()
        os.environ.update(env)

def read_file(f, *argc, **kwargs):
    with open(f, *argc, **kwargs) as f:
        return f.read()


class CompiledFunctionDelegator:
    def __init__(self, build_result, function_name=None):
        self.build_result = build_result
        if function_name is None:
            function_name = build_result.get_default_function_name()

        self.function_name = function_name

    def __getattr__(self, name):
        attr = getattr(self.build_result, name)
        if callable(attr):
            def redirect_to_build_result(*args, **kwargs):
                return attr(self.function_name, *args, **kwargs)
            return redirect_to_build_result
        else:
            return attr


def type_check(value, the_type):
    if not isinstance(value, the_type):
        raise ValueError(f"Expected '{the_type.__name__}' not '{type(value).__name__}' in {value}")

def type_check_list(values, the_type):
    if not all(isinstance(v, the_type) for v in values):
        raise ValueError(f"Expected sequence of '{the_type.__name__}' not '{[type(v).__name__ for v in values]}' in {values}")
    
