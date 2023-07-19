from cfiddle import *
from util import *
from cfiddle.Runner import Runner, DirectRunner, BashExecutionMethod, SubprocessExecutionMethod, InvocationDescription, IncorrectArgumentType, InvalidInvocation, RunOptionInterpreter, InvalidRunOption
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


@pytest.mark.parametrize("ExternalCommandRunner", [BashExecutionMethod,
                                                   SubprocessExecutionMethod])
def test_run_delegates(test_cpp, ExternalCommandRunner):
    from test_full_flow import test_run_combo
    with cfiddle_config(ExternalCommandRunner_type=ExternalCommandRunner):
        test_run_combo(test_cpp)


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

@pytest.mark.parametrize("Runner_type", [(DirectRunner),
                                         (Runner)])
def test_output(setup, capfd, Runner_type):

    with cfiddle_config(Runner_type=Runner_type):
        r = run(build(code(r"""
    #include<iostream>

    extern "C" void go() {
        std::cout << "hello\n";
        std::cerr << "world\n";
    }
    """)), "go")

    captured = capfd.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == "world\n"

    
def test_DirectRunner(test_cpp):
    with direct_execution():
        r = run(test_cpp, 'sum', arg_map(a=0,b=1))
        assert r[0].return_value == 1
        
def test_run_option_manager(setup):
    
    class MyException(Exception):
        pass

    class ROM(RunOptionInterpreter):
        def apply_options(self):
            raise MyException()
    
    with cfiddle_config(RunOptionInterpreter_type=ROM, Runner_type=DirectRunner):
        with pytest.raises(MyException):
            sanity_test()
    
def test_input_files(test_cpp):
    assert len(test_cpp.compute_input_files())== 1
    assert ".so" in test_cpp.compute_input_files()[0]

    r = run(test_cpp, 'sum', arg_map(a=0,b=1))
    assert len(r[0].invocation.compute_input_files()) == 1

    r = run(test_cpp, 'sum', arg_map(a=0,b=1), extra_input_files=["test_src/test.cpp"])
    assert len(r[0].invocation.compute_input_files()) == 2
    assert "test_src/test.cpp" in r[0].invocation.compute_input_files()

    r = run(test_cpp, 'sum', arg_map(a=0,b=1), extra_input_files=["test_src/*.cpp"])
    assert len(r[0].invocation.compute_input_files()) == 6
    
    with pytest.raises(InvalidInvocation):
        r = run(test_cpp, 'sum', arg_map(a=0,b=1), extra_input_files="foo")

def test_output_files(test_cpp):
    r = run(test_cpp, 'sum', arg_map(a=0,b=1), extra_output_files=["foo"])
    
    assert len(r[0].invocation.compute_output_files()) == 1
    
