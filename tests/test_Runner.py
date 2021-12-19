from fiddle.Runner import Runnable, Runner
from fiddle.ProtoParser import Prototype, Parameter
import ctypes
import pytest
import inspect

def test_create_runnable():

    runnable = Runnable("funtion", dict())

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
def test_bind_arguments(params, proto, result):
    runner = Runner(None)
    
    if inspect.isclass(result) and issubclass(result, Exception):
        with pytest.raises(result):
            runner.bind_arguments(params, proto)
    else:
        assert list(map(lambda x : x.value, runner.bind_arguments(params, proto))) == result


