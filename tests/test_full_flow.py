from fiddle import *
from fixtures import *
from itertools import product
from fiddle.Runner import InvocationResult

import pandas as pd
import numpy as np

def test_simplest():
    assert sanity_test() == 4

def test_one():

    build = ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0"))

    executable = MakeBuilder(build, verbose=True).build()

    invocation = InvocationDescription(executable, function="ordered", arguments=dict(count=1))

    result = LocalRunner(invocation).run()

    print(result.results)

    
def test_everything_explicit():

    exec_specs = [ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0")),
                  ExecutableDescription("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O1"))]

    executables = [MakeBuilder(es, verbose=True).build() for es in exec_specs]
    
    invocation_specs = [InvocationDescription(executables[0], function="ordered", arguments=dict(count=1)),
                        InvocationDescription(executables[1], function="ordered", arguments=dict(count=2)),
                        InvocationDescription(executables[0], function="ordered", arguments=dict(count=1)),
                        InvocationDescription(executables[1], function="ordered", arguments=dict(count=2))]
    
    results = [LocalRunner(i).run() for i in invocation_specs]

    print(InvocationResultsList(results).as_json())


def test_maps_experiment():

    executables = [MakeBuilder(ExecutableDescription("test_src/std_maps.cpp", build_parameters=p), verbose=True, rebuild=True).build()
                               for p in map_product(OPTIMIZE=["-O0", "-O3"])]

    invocations = [InvocationDescription(*i) for i in product(executables, ["ordered", "unordered"],map_product(count=map(lambda x: 2**x, range(0,10))))]

    results = InvocationResultsList(LocalRunner(i).run() for i in invocations)
    
    print(results.as_df())
    return results.as_df()

def test_build_wrappers():

        
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
              build_parameters=map_product(OPTIMIZE=["-O0", "-O3"]),
              verbose=True)
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert t[1].build_spec.build_parameters == dict(OPTIMIZE="-O3")
    assert len(t) == 2
    
    
def test_run_wrappers(test_cpp):
    
    for t in [run_one(test_cpp, "four"),
              run_one(test_cpp, "sum", dict(a=2, b=2)),
              run_one(exe=test_cpp, function="sum", arguments=dict(a=2, b=2))]:
        assert isinstance(t, InvocationResult)
        assert t.return_value == 4

    t = run(invocations=[(test_cpp, "sum", dict(a=1, b=2))])
    assert len(t) == 1
    assert t[0].return_value == 3
    
    t = run(invocations=product([test_cpp],
                                ["sum", "product"],
                                map_product(a=[1,2], b=[3,4])))
    assert len(t) == 8
    assert t[1].return_value == 5


def test_streamline():

    executables = build(source="test_src/std_maps.cpp",
                        build_parameters=map_product(OPTIMIZE=["-O0", "-O3"]),
                        verbose=True, rebuild=True)

    results = run(invocations=product(executables,
                                      ["ordered", "unordered"],
                                      map_product(count=map(lambda x: 2**x, range(0,10)))))
    print(results.as_df())
    

def _test_summarize():
    build.verbose()
    builds = build("test_src/std_maps.cpp", build_parameters=[], OPTIMIZE=["-O0", "-O1"])
    
    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=map_product(count=map(lambda x: 2**x, range(0,2))))
    

    results.as_csv("out.csv")
    with open("out.csv") as t:
        print(t.read())
    results.as_json("out.json")
    with open("out.json") as t:
        print(t.read())
    df = results.as_df()
    print(df)

    

def test_factoring_out_loops():
    for OPTIMIZE in ["-O0", "-O3"]:
        build = build_one("test_src/std_maps.cpp", dict(OPTIMIZE=OPTIMIZE))
        for function in ["ordered", "unordered"]:
            run(invocations=product([build],
                                    [function],
                                    map_product(count=map(lambda x: 2**x, range(0, 4)))))

