from fiddle import *
from itertools import product

import pandas as pd
import numpy as np


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
                               for p in expand_args(OPTIMIZE=["-O0", "-O3"])]

    invocations = [InvocationDescription(*i) for i in product(executables, ["ordered", "unordered"],expand_args(count=map(lambda x: 2**x, range(0,10))))]

    results = InvocationResultsList(LocalRunner(i).run() for i in invocations)
    
    print(results.as_df())
    

def test_build_wrappers():

        
    t = build("test_src/std_maps.cpp")
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1

    t = build_one("test_src/std_maps.cpp")
    assert t.build_spec.build_parameters == {}
    assert isinstance(t, Executable)
    
    t = build("test_src/std_maps.cpp",
              verbose=True, rebuild=True)
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1
    
    t = build(source="test_src/std_maps.cpp",
              parameters={},
              verbose=True, rebuild=True)
    assert t[0].build_spec.build_parameters == {}
    assert len(t) == 1
    
    t = build(source="test_src/std_maps.cpp",
              parameters=dict(OPTIMIZE="-O0"),
              verbose=True, rebuild=True)
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert len(t) == 1
    
    t = build(source="test_src/std_maps.cpp",
              parameters=expand_args(OPTIMIZE=["-O0", "-O3"]),
              verbose=True, rebuild=True)
    assert t[0].build_spec.build_parameters == dict(OPTIMIZE="-O0")
    assert t[1].build_spec.build_parameters == dict(OPTIMIZE="-O3")
    assert len(t) == 2
    
    
def test_run_wrappers():
    
    executables = build("test_src/test.cpp", rebuild=True)
    
    t = run(executables[0], "four")
    assert len(t) == 1

    t = run(executables[0], "sum", dict(a=1, b=2))
    assert len(t) == 1

    t = run(exe=executables[0], function="sum", arguments=dict(a=1, b=2))
    assert len(t) == 1

    t = run(invocations=[(executables[0], "sum", dict(a=1, b=2))])
    assert len(t) == 1
    
    t = run(invocations=product(executables,
                                     ["sum", "product"],
                                     expand_args(a=[1,2], b=[3,4])))
    assert len(t) == 8
    

def test_streamline():

    executables = build(source="test_src/std_maps.cpp",
                        parameters=expand_args(OPTIMIZE=["-O0", "-O3"]),
                        verbose=True, rebuild=True)

    results = run(invocations=product(executables,
                                      ["ordered", "unordered"],
                                      expand_args(count=map(lambda x: 2**x, range(0,10)))))
    print(results.as_df())
    

def _test_summarize():
    build.verbose()
    builds = build("test_src/std_maps.cpp", parameters=[], OPTIMIZE=["-O0", "-O1"])
    
    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,2))))
    

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
                                    expand_args(count=map(lambda x: 2**x, range(0, 4)))))

