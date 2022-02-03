import pytest
import copy
import sys
import os
from contextlib import contextmanager
from collections.abc import Iterable
import subprocess
import time


def arg_map(**parameters):
    """Generates the `named cross product` for a :obj:`dict` that maps names to lists of values.  

    For example:


    .. doctest::

      >>> from cfiddle import *
      >>> from pprint import pprint
      >>> pprint(arg_map(foo=[1,2], bar=[3,4], baz=5))
      [{'bar': 3, 'baz': 5, 'foo': 1},
       {'bar': 4, 'baz': 5, 'foo': 1},
       {'bar': 3, 'baz': 5, 'foo': 2},
       {'bar': 4, 'baz': 5, 'foo': 2}]
   
    Args:
      **kwargs: key-value pairs.  Scalar values will are treated as lists of length 1.

    Returns:
      :obj:`list` of :obj:`dict`:  See example above.

    """
    def listify(t):
        return t if isinstance(t, Iterable) and not isinstance(t, str) and not isinstance(t, dict) else [t]
    t = [(k, listify(v)) for k,v in parameters.items()]
    return _cross_product(t)

def infer_language(filename):
    suffixes_to_language = {".CPP" : "c++",
                            ".cpp" : "c++",
                            ".cc" : "c++",
                            ".cp" : "c++",
                            ".c++" : "c++",
                            ".cxx" : "c++",
                            ".C" : "c++",
                            ".ii" : "c++",
                            ".c" : "c",
                            ".i" : "c",
                            ".go": "go"}

    _, ext = os.path.splitext(filename)
    try:
        return suffixes_to_language[ext]
    except KeyError:
        raise ValueError(f"I don't know what language {filename} is written in.")



def exp_range(low, high, multiplier=2):
    last = None
    while low < high:
        if last != int(low):
            last = int(low)
            yield int(low)
        low = low * multiplier
    yield int(low)    

    
def changes_in(filename):
    last_mtime = None
    while True:
        current_mtime  = os.path.getmtime(filename)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            yield filename
        time.sleep(0.5)

        
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


def invoke_process(cmd, stdin=None):
    try:
        p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=stdin)
        return True, p.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()
    except FileNotFoundError as e:
        return False, str(e)

    
def get_native_architecture():
    return os.uname().machine
    
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
        os.chdir(path)
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
    def __init__(self, build_result, function_name):
        self.build_result = build_result

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
        raise TypeError(f"Expected '{the_type.__name__}' not '{type(value).__name__}' in {value}")

def type_check_list(values, the_type):
    if not all(isinstance(v, the_type) for v in values):
        raise TypeError(f"Expected sequence of '{the_type.__name__}' not '{[type(v).__name__ for v in values]}' in {values}")
    

def running_under_jupyter():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules
