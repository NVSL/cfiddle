from .CProtoParser import CProtoParser
from .Parameters import  bind_parameters
from .util import expand_args
from .Runner import Runnable, to_csv
from .LocalRunner import LocalRunner, run
from .MakeBuilder import MakeBuilder, build
import sys

def dump(x):
    print("\n".join(map(str,x)))

def test_summarize():
    builds = build("test_src/std_maps.cpp", OPTIMIZE="-O0")

    results = run(build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,2))))

    results.csv("out.csv")
    with open("out.csv") as t:
        print(t.read())
    results.json("out.json")
    with open("out.json") as t:
        print(t.read())
    df = results.df()
    print(df)
    
    
def test_maps():
    builds = build("test_src/std_maps.cpp", OPTIMIZE=["-O0", "-O1", "-O3", "-Og"])

    results = run((builds[0], "ordered", dict(count=24)),
                  build=builds,
                  function=["ordered", "unordered"],
                  arguments=expand_args(count=map(lambda x: 2**x, range(0,20))))

    to_csv("out.csv", results)
