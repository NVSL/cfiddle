from fiddle.util import expand_args
from fiddle.LocalRunner import run
from fiddle.MakeBuilder import build
import os

def dump(x):
    print("\n".join(map(str,x)))

def test_summarize():
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
    
def test_maps():
    from pandas import DataFrame

    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O1", "-O3", "-Og"])

    results = run((builds[0], "ordered", dict(count=24)),
                  build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,20))))

    results.as_csv("out.csv")
    assert os.path.exists("out.csv")
    assert isinstance(results.as_df(), DataFrame)
    
    return results.as_df()

def test_df_numeric_conversion():
    builds = build(code="""
#include"fiddle.hpp"

extern "C"
void go() {
    get_dataset()->start_new_row();
    get_dataset()->set("a", 4);
    get_dataset()->set("b", 5.0);
}
""")

    results = run((builds, "go", dict()))

    df = results.as_df()

    # Shouldn't fail
    df["a"]  = df["a"] + 1
    df["b"]  = df["b"] + 1.0
    

    

def test_optimization_maps():

    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O3"])

    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0, 22))))
    
    return results.as_df()

def test_factoring_out_loops():
    for OPTIMIZE in ["-O0", "-O3"]:
        for function in ["ordered", "unordered"]:
            builds = build("test_src/std_maps.cpp", OPTIMIZE=[OPTIMIZE])
            results = run(build=[builds],
                          function=[function],
                          arguments=expand_args(count=map(lambda x: 2**x, range(0, 20))))

