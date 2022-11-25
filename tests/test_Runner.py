from cfiddle import *
from util import *
from cfiddle.Runner import Runner, InvocationDescription, IncorrectArgumentType, InvalidInvocation, RunOptionManager
from fixtures import *
import ctypes
import pytest
import inspect
import os

from cfiddle.ProtoParser import Parameter, Prototype

test_prototype = Prototype(None, None, (Parameter(type=ctypes.c_float, name="a"),
                                        Parameter(type=ctypes.c_int, name="b")))

@pytest.mark.parametrize("params,proto,result", [
    (dict(a=1, b=2),
     test_prototype,
     [1,2]),
    (dict(a=object(), b=2),
     test_prototype,
     IncorrectArgumentType),
    (dict(a="aoeu", b=2),
     test_prototype,
     IncorrectArgumentType),
    (dict(a="aoeu", b=2),
     test_prototype,
     IncorrectArgumentType)
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


def test_Invocation_types(test_cpp):
    with pytest.raises(InvalidInvocation):
        InvocationDescription(1,1,1)
    
    with pytest.raises(InvalidInvocation):
        InvocationDescription(test_cpp,"",{1:1})

    with pytest.raises(InvalidInvocation):
        InvocationDescription(test_cpp,"",{1:1})

    with pytest.raises(InvalidInvocation):
        InvocationDescription(test_cpp,"",dict(a=1),perf_counters="a")

    with pytest.raises(InvalidInvocation):
        InvocationDescription(test_cpp,"",dict(a=1),perf_counters=[["a"]])

    with pytest.raises(InvalidInvocation):
        InvocationDescription(test_cpp,"",dict(a=1),perf_counters=[["a"]])

@pytest.fixture
def env_echo(setup):
    return build(code(r"""
#include<stdlib.h>
extern "C" long int env() {
    return strtol(getenv("NUMBER"), NULL, 10);
}"""))[0]
   

def test_run_options(env_echo):
    enable_debug()
 
    os.environ["NUMBER"] = "6"
    run(env_echo, function="env")[0].return_value == 6
    run(env_echo, function="env",
        run_options=dict(NUMBER=4))[0].return_value == 4
    run(env_echo, function="env")[0].return_value == 6
    
    t = run(env_echo, function="env",
            run_options=arg_map(NUMBER=[1,2,4]))


    assert (t[0].return_value, t[1].return_value, t[2].return_value) == (1,2,4)

def test_default_run_options(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=[1,2])):
        t = run(env_echo, function="env")
        assert t[0].return_value == 1
        assert t[1].return_value == 2

    
def test_run_option_manager(setup):
    
    class MyException(Exception):
        pass

    class ROM(RunOptionManager):
        def apply_options(self):
            raise MyException()
        
    with cfiddle_config(RunOptionManager_type=ROM):
        with pytest.raises(MyException):
            sanity_test()
    
