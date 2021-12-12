import pytest
import copy
import os
from contextlib import contextmanager
from collections.abc import Iterable
import subprocess

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
    os.environ.update(**kwds)
    try:
        yield None
    finally:
        os.environ.clear()
        os.environ.update(env)

def cross_product(parameters):
    if len(parameters) == 0:
        return []
    if len(parameters) == 1:
        name, values = parameters[0]
        return [{name:v} for v in values]
    
    ret = []
    rest = cross_product(parameters[:-1])
    name, values = parameters[-1]
    for r in rest:
        for v in values:
            t = copy.copy(r)
            t[name] = v
            ret.append(t)
            
    return ret

def expand_args(**parameters):
    """
    Generate a set of parameter assignments from a dict or parameter names and values.

    expand_args(dict(a=range(1,3),
                b=1)

    yields:

    [{"a": 1, "b": 1},  {"a": 2, "b": 1}])

    """
    def listify(t):
        return t if isinstance(t, Iterable) and not isinstance(t, str) else [t]
    t = [(k, listify(v)) for k,v in parameters.items()]
    print(t)
    return cross_product(t)
        

def invoke_process(cmd):
    try:
        p = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        return True, p.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()

@pytest.mark.parametrize("inp,output", [
    (dict(), []),
    (dict(a=1), [{"a": 1}]),
    (dict(a="bc"), [{"a": "bc"}]),
    (dict(a=[1,2]), [{"a": 1},
                     {"a": 2}]),
    (dict(a=range(1,3),
          b=1), [{"a": 1, "b": 1},
                 {"a": 2, "b":1}]),
    (dict(a=(1,2), b=[3,4]), [
        {"a": 1,
         "b": 3},
        {"a": 1,
         "b": 4},
        {"a": 2,
         "b": 3},
        {"a": 2,
         "b": 4}]),
    (dict(a=1,b=2,c=3),
     [ {"a": 1,
        "b": 2,
        "c": 3}]),
    (dict(a=[1],b=[2],c=[3]),
     [ {"a": 1,
        "b": 2,
        "c": 3}])
])
def test_expand_args(inp, output):
    assert expand_args(**inp) == output
