from cfiddle import *
from util import *
from fixtures import *
from itertools import product
from cfiddle.Runner import InvocationResult

import pandas as pd
import numpy as np

@pytest.mark.smoke
def test_simplest(setup):
    assert sanity_test() == 4

def test_one(setup):

    build = ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0"))

    executable = MakeBuilder(build, verbose=True).build()

    invocation = InvocationDescription(executable, function="ordered", arguments=dict(count=1))

    result = LocalSingleRunner(invocation).run()

    print(result.results)

    
def test_everything_explicit(setup):

    exec_specs = [ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0")),
                  ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O1"))]

    executables = [MakeBuilder(es, verbose=True).build() for es in exec_specs]
    
    invocation_specs = [InvocationDescription(executables[0], function="ordered", arguments=dict(count=1)),
                        InvocationDescription(executables[1], function="ordered", arguments=dict(count=2)),
                        InvocationDescription(executables[0], function="ordered", arguments=dict(count=1)),
                        InvocationDescription(executables[1], function="ordered", arguments=dict(count=2))]
    
    results = Runner(invocation_specs).run()

    print(InvocationResultsList(results).as_json())


def check_for_compiler(c):
    success, _ = invoke_process([c, "-v"])
    if not success:
        pytest.skip(f"Compiler {c} is not available.")
        
@pytest.mark.parametrize("compiler", ["g++", "clang++"])
def test_maps_experiment(setup, compiler):
    check_for_compiler(compiler)
    b = build("test_src/std_maps.cpp", arg_map(OPTIMIZE=["-O0", "-O3"], CXX=compiler), verbose=True)
    results = run(b, ["ordered", "unordered"], arg_map(count=exp_range(1,1024,2)))
    
    print(results.as_df())
    return results.as_df()

def test_build_simple(setup):
        
    t = build("test_src/std_maps.cpp", rebuild=True)
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1

    t = build_one("test_src/std_maps.cpp")
    assert t.build_spec.build_parameters == {}
    assert isinstance(t, Executable)
    
    t = build("test_src/std_maps.cpp",
              verbose=True)
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1

def test_build_parameter(setup):
    
    t = build(source="test_src/std_maps.cpp",
              build_parameters={},
              verbose=True)
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1
    
    t = build(source="test_src/std_maps.cpp",
              build_parameters=dict(OPTIMIZE="-O0"),
              verbose=True)
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert len(t) == 1
    
    t = build(source="test_src/std_maps.cpp",
              build_parameters=arg_map(OPTIMIZE=["-O0", "-O3"]),
              verbose=True)
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert t[1].build_spec.build_parameters == dict(OPTIMIZE="-O3")
    assert len(t) == 2


def test_build_multi_build(setup):
    t = build(source=["test_src/std_maps.cpp","test_src/test.cpp"],
              build_parameters=arg_map(OPTIMIZE=["-O0", "-O1"]))
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert t[2].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert len(t) == 4
    
    
    
def test_run_one(test_cpp):
    
    for t in [run_one(test_cpp, "four"),
              run_one(test_cpp, "sum", dict(a=2, b=2)),
              run_one(exe=test_cpp, function="sum", arguments=dict(a=2, b=2))]:
        assert isinstance(t, InvocationResult)
        assert t.return_value == 4

        
def test_run_list(test_cpp):
    t = run_list(invocations=[dict(executable=test_cpp, function="sum", arguments=dict(a=1, b=2))])
    assert len(t) == 1
    assert t[0].return_value == 3
    
    t = run_list(invocations=arg_map(executable=[test_cpp],
                                     function=["sum", "product"],
                                     arguments=arg_map(a=[1,2], b=[3,4])))
    assert len(t) == 8
    assert t[1].return_value == 5

    
def test_run_simple(test_cpp):

    t = run(executable=test_cpp, function="sum", arguments=dict(a=1, b=2))
    assert len(t) == 1
    assert t[0].return_value == 3


def test_run_combo(test_cpp):
    t = run(executable=test_cpp,
             function=["sum", "product"],
             arguments=arg_map(a=[1,2], b=[3,4]))
    
    assert len(t) == 8
    assert t[1].return_value == 5

def test_no_args(test_cpp):
    t = run(executable=[test_cpp,test_cpp],
            function=["nop", "four"])
    
    assert len(t) == 4
    assert t[0].return_value == 4
    assert t[1].return_value == 4
    assert t[2].return_value == 4
    assert t[3].return_value == 4

    
def test_streamline(setup):

    executables = build(source="test_src/std_maps.cpp",
                        build_parameters=arg_map(OPTIMIZE=["-O0", "-O3"]),
                        verbose=True, rebuild=True)

    results = run(executable=executables,
                  function=["ordered", "unordered"],
                  arguments=arg_map(count=map(lambda x: 2**x, range(0,10))))
    print(results.as_df())
    
