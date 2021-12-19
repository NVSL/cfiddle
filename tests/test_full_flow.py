from fiddle.Builder import BuildSpec
from fiddle.MakeBuilder import MakeBuilder
from fiddle.LocalRunner import LocalRunner
from fiddle.Runner import Invocation, Runnable
from fiddle.source import Assembly, Preprocessed, Source
from fiddle.Data import InvocationResultsList

import pandas as pd
import numpy as np


def test_one():

    build = BuildSpec("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0"))

    invocations_spec = Runnable(function="ordered", arguments=dict(count=1))
    
    executable = MakeBuilder(build, verbose=True).build()

    invocation = Invocation(executable, invocations_spec)

    result = LocalRunner(invocation).run()

    print(result.results)

    
def test_everything_explicit():

    builds = [BuildSpec("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O0")),
              BuildSpec("test_src/std_maps.cpp", build_parameters=dict(OPTIMIZE="-O1"))]

    invocation_spec = [Runnable(function="ordered", arguments=dict(count=1)),
                        Runnable(function="ordered", arguments=dict(count=2))]

    executables = [MakeBuilder(b, verbose=True).build() for b in builds]

    invocations = [
        Invocation(executables[0], invocation_spec[0]),
        Invocation(executables[0], invocation_spec[1]),
        Invocation(executables[1], invocation_spec[0]),
        Invocation(executables[1], invocation_spec[1]),
    ]

    results = [LocalRunner(i).run() for i in invocations]

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

