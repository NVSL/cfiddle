from cfiddle import *
from util import *
from cfiddle.Runner import Runner, InvocationDescription, IncorrectArgumentType, InvalidInvocation, RunOptionManager, InvalidRunOption
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
    long int a = 0;
    long int b = 0;
    if (getenv("NUMBER"))
         a = strtol(getenv("NUMBER"), NULL, 10);
    if (getenv("NUMBER2"))
         b = strtol(getenv("NUMBER2"), NULL, 10);
    return a + b;
}"""))[0]
   

def test_run_options(env_echo):
    enable_debug()
 
    os.environ["NUMBER"] = "6"
    run(env_echo, function="env")[0].return_value == 6
    run(env_echo, function="env",
        run_options=arg_map(NUMBER=4))[0].return_value == 4
    run(env_echo, function="env")[0].return_value == 6
    
    t = run(env_echo, function="env",
            run_options=arg_map(NUMBER=[1,2,4]))

    assert (t[0].return_value, t[1].return_value, t[2].return_value) == (1,2,4)

def test_default_run_options(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=[1,2])):
        t = run(env_echo, function="env")
        assert t[0].return_value == 1
        assert t[1].return_value == 2

def test_default_run_option5(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=[1,2])):
        t = run(env_echo, function="env", run_options = arg_map(NUMBER2=10))
        assert t[0].return_value == 11
        assert t[1].return_value == 12

def test_default_run_options2(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=1)):
        t = run(env_echo, function="env", run_options=arg_map(NUMBER2=[1,2]))
        assert len(t) == 2
        assert t[0].return_value == 2
        assert t[1].return_value == 3

def test_default_run_options3(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=[10,20])):
        t = run(env_echo, function="env", run_options=arg_map(NUMBER=30, NUMBER2=[1,2]))
        assert len(t) == 4
        assert t[0].return_value == 31
        assert t[1].return_value == 32
        assert t[2].return_value == 31
        assert t[3].return_value == 32

def test_default_run_options4(env_echo):
    with cfiddle_config(run_options_default=arg_map(NUMBER=[10,20], NUMBER2=[4,5])):
        t = run(env_echo, function="env", run_options=arg_map(NUMBER=30, NUMBER2=[1,2]))
        assert len(t) == 8
        assert t[0].return_value == 31
        assert t[1].return_value == 32
        assert t[2].return_value == 31
        assert t[3].return_value == 32
        assert t[4].return_value == 31
        assert t[5].return_value == 32
        assert t[6].return_value == 31
        assert t[7].return_value == 32

def test_invalid_run_options(env_echo):

    with pytest.raises(InvalidRunOption):
        run(env_echo, "env", run_options={"boo":"bar"})

    
    
def test_run_option_manager(setup):
    
    class MyException(Exception):
        pass

    class ROM(RunOptionManager):
        def apply_options(self):
            raise MyException()
    
    with cfiddle_config(RunOptionManager_type=ROM, Runner_type=Runner):
        with pytest.raises(MyException):
            sanity_test()
    
