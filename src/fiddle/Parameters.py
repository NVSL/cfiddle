import pytest
import copy
import ctypes
from collections import OrderedDict
from .ProtoParser import Prototype, Parameter
import inspect

class UnusedParameter(Exception):
    pass

class MissingParameter(Exception):
    pass

def bind_parameters(parameters, signature):
    """
    Take mapping from parameter names to values a function signature and:
    1.  Check that the values of the parameters are compatible with the signature
    2.  Return an parameter list in the right order to call the function.
    """
    r = []
    for a in signature.parameters:
        if a.name not in parameters:
            raise MissingParameter(a.name)
        
        r.append(a.type(parameters[a.name]))
    for p in parameters:
        if not any(map(lambda x: x.name == p, signature.parameters)):
            raise UnusedParameter(p)
    return r

test_prototype = Prototype(None, None, (Parameter(type=ctypes.c_float, name="a"),
                                        Parameter(type=ctypes.c_int, name="b")))

@pytest.mark.parametrize("params,proto,result", [
    (dict(a=1, b=2),
     test_prototype,
     [1,2]),
    (dict(a=object(), b=2),
     test_prototype,
     TypeError),
    (dict(a="aoeu", b=2),
     test_prototype,
     TypeError),
    (dict(a="aoeu", b=2),
     test_prototype,
     TypeError)
]
)
def test_bind_parameters(params, proto, result):
    if inspect.isclass(result) and issubclass(result, Exception):
        with pytest.raises(result):
            bind_parameters(params, proto)
    else:
        assert list(map(lambda x : x.value, bind_parameters(params, proto))) == result

        

