import pytest
import copy
import sys
import os

from contextlib import contextmanager
from functools import reduce
from itertools import product
from collections.abc import Iterable
import subprocess
import time

from .Exceptions import CFiddleException

def arg_map(**parameters):
    """Generates take a set of named lists of values and generate the
    `named cross product` a set of :obj:`dict` s with all combinations of
    the values.

    For example:

    .. doctest::

      >>> from cfiddle import *
      >>> from pprint import pprint
      >>> pprint(arg_map(foo=[1,2], bar=[3,4], baz=5))
      [{'bar': 3, 'baz': 5, 'foo': 1},
       {'bar': 4, 'baz': 5, 'foo': 1},
       {'bar': 3, 'baz': 5, 'foo': 2},
       {'bar': 4, 'baz': 5, 'foo': 2}]

    You can also specify a list argument values by adding together the results of :func:`arg_map`:

    .. doctest::

      >>> from cfiddle import *
      >>> from pprint import pprint
      >>> pprint(arg_map(foo=1, bar=3, baz=5) +
      ...        arg_map(foo=4, bar=5, baz=6))
      [{'bar': 3, 'baz': 5, 'foo': 1}, {'bar': 5, 'baz': 6, 'foo': 4}]


    Args:
      **kwargs: key-value pairs.  Scalar values will are treated as lists of length 1.

    Returns:
      :obj:`list` of :obj:`dict`:  See example above.

    """
    
    def listify_value(t):
        return t if isinstance(t, Iterable) and not isinstance(t, str) and not isinstance(t, dict) else [t]
    
    def ensure_value_is_iterable(p):
        return {k: listify_value(v) for k,v in p.items()}
    def expand_parameter_values(arg,values):
        return [{arg:v} for v in values]
    
    parameters = ensure_value_is_iterable(parameters)
    expanded = [expand_parameter_values(k,v) for k,v in parameters.items()]
    
    return list(arg_product(*expanded))

def arg_product(*args):
    """Generate and merge the cross product of a set of dicts.  The arguments must be lists of :obj:`dict`.

    In the common use case, the arguments are the result of calls to
    :func:`arg_map`.

    For example:

    .. doctest::

      >>> from cfiddle import *
      >>> from pprint import pprint
      >>> pprint(arg_map(a=[1,2]))
      [{'a': 1}, {'a': 2}]
      >>> pprint(arg_map(b=[3,4]))
      [{'b': 3}, {'b': 4}]
      >>> pprint(arg_product(arg_map(a=[1,2]), arg_map(b=[3,4])))
      [{'a': 1, 'b': 3}, {'a': 1, 'b': 4}, {'a': 2, 'b': 3}, {'a': 2, 'b': 4}]

    You can use :func:`arg_product` and :func:`arg_map` to compose
    complex combinations of parameters.  

    For instance, let's imagine that we a C++ function,
    
    .. code::
      
      matexp(int m, int tile_size, int thread_count)

    that measures the performance of raising an
    :code:`m` x :code:`m` matrix to the :code:`p` th power using a given
    memory :code:`tile_size` and :code:`thread_count`.

    We'd like to chose a few representative values of :code:`m` and
    :code:`p` and run them for all combinations of
    :code:`thread_count` and :code:`tile_size`.

    We can the set of function arguments like so:

    .. doctest::

      >>> from cfiddle import *
      >>> from pprint import pprint
      >>> p = arg_product(arg_map(size=600, power=2) + 
      ...                 arg_map(size=320, power=40) + 
      ...                 arg_map(size=120, power=240), 
      ...                 arg_map(thread_count=[1,2], 
      ...                         tile_size=[4,8,16]))
      >>> pprint(p)  # doctest: +SKIP
      [{'power': 2, 'size': 600, 'thread_count': 1, 'tile_size': 4},
       {'power': 2, 'size': 600, 'thread_count': 1, 'tile_size': 8},
       {'power': 2, 'size': 600, 'thread_count': 1, 'tile_size': 16},
       {'power': 2, 'size': 600, 'thread_count': 2, 'tile_size': 4},
       {'power': 2, 'size': 600, 'thread_count': 2, 'tile_size': 8},
       {'power': 2, 'size': 600, 'thread_count': 2, 'tile_size': 16},
       {'power': 40, 'size': 320, 'thread_count': 1, 'tile_size': 4},
       {'power': 40, 'size': 320, 'thread_count': 1, 'tile_size': 8},
       {'power': 40, 'size': 320, 'thread_count': 1, 'tile_size': 16},
       {'power': 40, 'size': 320, 'thread_count': 2, 'tile_size': 4},
       {'power': 40, 'size': 320, 'thread_count': 2, 'tile_size': 8},
       {'power': 40, 'size': 320, 'thread_count': 2, 'tile_size': 16},
       {'power': 240, 'size': 120, 'thread_count': 1, 'tile_size': 4},
       {'power': 240, 'size': 120, 'thread_count': 1, 'tile_size': 8},
       {'power': 240, 'size': 120, 'thread_count': 1, 'tile_size': 16},
       {'power': 240, 'size': 120, 'thread_count': 2, 'tile_size': 4},
       {'power': 240, 'size': 120, 'thread_count': 2, 'tile_size': 8},
       {'power': 240, 'size': 120, 'thread_count': 2, 'tile_size': 16}]

    Args:
      *args: A list of :obj:`dict`.

    Returns:
      :obj:`list` of :obj:`dict`

    """
    r = []
    
    if len(args) == 0:
        return [{}]

    
    for a in args:
        try:
            type_check_list(a, dict)
        except TypeError:
            raise ArgProductError(f"Arguments to arg_product(), must be list of dicts, not {a}")
            
    def merge(a,b):
        a.update(b)
        return a
    
    return [reduce(merge, copy.deepcopy(arg)) for arg in product(*args)]


def infer_language(filename):
    suffixes_to_language = {".CPP" : "c++",
                            ".cpp" : "c++",
                            ".cc" : "c++",
                            ".cp" : "c++",
                            ".c++" : "c++",
                            ".cxx" : "c++",
                            ".hpp" : "c++",
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
        n = int(round(low))
        if last != n:
            last = n
            yield n
        low = low * multiplier
    yield int(round(low))

    
def changes_in(filename):
    last_mtime = None
    while True:
        current_mtime  = os.path.getmtime(filename)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            yield filename
        time.sleep(0.5)

        

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

def write_file(f, contents, mode="w", *argc, **kwargs):
    with open(f, mode, *argc, **kwargs) as f:
        return f.write(contents)

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
    if isinstance(values, str):
        raise TypeError(f"Expected iterable object (other than a str), not '{type(values).__name__}'")
    
    try:
        iter(values)
    except:
        raise TypeError(f"Expected iterable object (other than a string), not '{type(values).__name__}'")
    
    if not all(isinstance(v, the_type) for v in values):
        raise TypeError(f"Expected sequence of '{the_type.__name__}' not '{[type(v).__name__ for v in values]}' in {values}")
    

def running_under_jupyter():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules



class ArgProductError(CFiddleException):
    pass
