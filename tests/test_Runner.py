from cfiddle import *
from util import *
from cfiddle.Runner import Runner, InvocationDescription
from fixtures import *
import ctypes
import pytest
import inspect

from cfiddle.ProtoParser import Parameter, Prototype

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
def test_bind_arguments(params, proto, result,setup):
    runner = Runner(None)
    
    if inspect.isclass(result) and issubclass(result, Exception):
        with pytest.raises(result):
            runner.bind_arguments(params, proto)
    else:
        assert list(map(lambda x : x.value, runner.bind_arguments(params, proto))) == result


def test_return_values(test_cpp):
    r = run_one(test_cpp, "four")
    assert r.return_value == 4


def test_InvocationDescription_types(test_cpp):
    with pytest.raises(ValueError):
        InvocationDescription(1,1,1)
    
    with pytest.raises(ValueError):
        InvocationDescription(test_cpp,"",{1:1})

    with pytest.raises(ValueError):
        InvocationDescription(test_cpp,"",{1:1})
