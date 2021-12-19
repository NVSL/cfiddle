from fiddle.Builder import ExecutableDescription
from fiddle.MakeBuilder import MakeBuilder
from fiddle.LocalRunner import LocalRunner
from fiddle.Runner import InvocationDescription
from fiddle.source import Assembly, Preprocessed, Source
from fiddle.Data import InvocationResultsList

import pandas as pd
import numpy as np

# ExecutableSpec
# Executable
# InvocationSpec = (Executable, function, arguments)
# InvocationResult


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


def _test_maps_experiment():
    
    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O1", "-O3", "-Og"])

    results = run((builds[0], "ordered", dict(count=24)),
                  build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,20))))

    results.as_csv("out.csv")
    assert os.path.exists("out.csv")
    assert isinstance(results.as_df(), DataFrame)
    
    return results.as_df()

    

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

    

def _test_optimization_maps():

    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O3"])

    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0, 22))))
    
    return results.as_df()


def _test_factoring_out_loops():
    for OPTIMIZE in ["-O0", "-O3"]:
        for function in ["ordered", "unordered"]:
            builds = build("test_src/std_maps.cpp", OPTIMIZE=[OPTIMIZE])
            results = run(build=[builds],
                          function=[function],
                          arguments=expand_args(count=map(lambda x: 2**x, range(0, 20))))

