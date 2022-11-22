from cfiddle import *
from util import *
from fixtures import *
from cfiddle.Runner import RunnerException

def test_hello_world(test_cpp):
    
    invocation = InvocationDescription(test_cpp, function="simple_print", arguments=dict(a=1, b=2, c=3))
    runner = LocalSingleRunner(invocation)
    invocation_result = runner.run()
    print(invocation_result.results)

def test_missing_function(test_cpp):
    invocation = InvocationDescription(test_cpp, function="missing", arguments=dict(a=1, b=2, c=3))
    with pytest.raises(RunnerException):
        runner = LocalSingleRunner(invocation).run()
    

def test_function_pointer(setup):
    import ctypes
    b = build(code(r"""
#include<iostream>
#include"cfiddle.hpp"
extern "C" void foo(int a) { std::cerr << "from foo: " << a << "\n";}
extern "C" void bar(int a) { std::cerr << "from bar: " << a << "\n";}


extern "C" int four(int a, funcptr_t f) { 
    std::cerr << "\n";
    std::cerr << (unsigned long long)f << "\n";
    std::cerr << (unsigned long long)foo << "\n";
    auto callee = (void(*)(int))(f);
    callee(a);
    return (unsigned long long)f == (unsigned long long)foo;
}

"""))

    c_lib = ctypes.CDLL(b[0].lib)
    t = getattr(c_lib, "foo")
    enable_debug()

    f = ctypes.pointer(t)

    proto = ctypes.CFUNCTYPE(ctypes.c_int)
    ff = proto(42)
    assert run(b, "four", arg_map(a=[4,8],
                                  f=["foo", "bar"]
                                  ))[0] != 0
    
