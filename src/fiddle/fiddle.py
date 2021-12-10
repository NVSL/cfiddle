from .CProtoParser import CProtoParser
from .Parameters import  bind_parameters
from .util import expand_args
from .Runner import Runnable
from .LocalRunner import LocalRunner
from .MakeBuilder import MakeBuilder
import sys

"""

Design notes:

Goals:
1.  Language independence
2.  Extensible 

Let's factor fiddles into several parts:

In python:

1.  File parser that extracts function prototypes from a source file. (`parse_prototype.py`).
    1.  return a set signatures you can called based on ctypes datatypes.
    2.  Language agnostic.
3.  A parameter generator that builds type-checked sets of parameters to use in compilation and to pass to a function in the .so file.
2.  A builder that converts source files into .so files ('Makefile').  
    1.  A makefile that can easily and correctly build an .so file (and intermediary files) in given build directory
    2.  A driver to invoke it with different compilation settings. 
4.  A Runner that takes a set of .so files and a set of configurations and runs them and generates a CSV file.
    1.  Merge output CSV and with configuration set. 
    2.  Subclass to run locally, via 'cse142 job run', via ssh.1
    3.  Also in charge of transfering files.
5.  A mechanism to easily compute derived metrics -- like calc.py.  Maybe based on pandas.  But the .cfg file mechanism is pretty great.

In C++:

1.  Library for storing a map between strings and arbitrary values collector.hpp and output them and output them as CSV files.
2.  A wrapper around libperf/PAPI to easily collect perf counts and time execution time.
3.  A library of simplified interfaces to set clock speed, flush caches, etc.

"""

def _test_this():
    source="test.cpp"
    function="simple_print_f"

    signatures = CProtoParser().parse_file(source)
    print(signatures)
    function_arguments = expand_args(a=[1,2],
                                     b=[3,1.2],
                                     c=[4,5])
    print("\n".join(map(str,function_arguments)))

    builds = MakeBuilder().build(source, parameters=expand_args(OPTIMIZE=["-O0", "-O1", "-O3", "-Og"]))

    print("\n".join(map(lambda x:x.lib, builds)))

    runnables = [Runnable(r["build"].lib, signatures[function], r["args"], build_parameters=r["build"].parameters)
                 for r in expand_args(build=builds, args=function_arguments)]

    print("\n".join(map(str, runnables)))

    results = LocalRunner().run(runnables)

    for a, r in zip(results, results):
        print("=============================")
        print(f"run =  {a}\n")
        print(f"results= {r.output.decode()}\n")

        # would rather write
        # r = LocalRunner.call(b.funcs.go, k=1)
        # or
        # r = b.go(k=1)
        # r = b.go(k=[1,2,3], z=[1,3,3])
        # from MakeBuilder import compile
        # since **kwargs is ordered in > python 3.6, we can specify parameter sweeps as kwargs
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", k=[1,2,3], z=[1,2,3])
        # r = compile("write_dataset.cpp", OPTIMIZE=["-O0", "-Og", "-O3"], GPROF=["yes", "no"]).run("go", k=[1,2,3], z=[1,2,3])
        # r = compile(src=r"""extern "C" void run("go", int k, int z) {} """, OPTIMIZE=["-O0", "-Og", "-O3"], GPROF=["yes", "no"]).run("go", k=[1,2,3], z=[1,2,3])
        # c = compile(src=r"""extern "C" void run("go", int k, int z) {} """, OPTIMIZE=["-O0", "-Og", "-O3"], GPROF=["yes", "no"])
        # display(c.go.cfg())  # see the cfg for the first build
        # display(c.go.asm(1)) # see th asm for the second build
        # display(c.build_params(1)) # see the build params for the first build
        # display(r.dataframe)
        #
        # How to specify the runner?
        #
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", runner=LocalRunner(), k=[1,2,3], z=[1,2,3])
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", runner=CSE142Runner(), k=[1,2,3], z=[1,2,3])
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", runner=CSE142Runner(MHz=[1000, 1100], flush_caches=[True, False]), k=[1,2,3], z=[1,2,3])

        # Want to run multiple functions:
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", k=[1,2,3], z=[1,2,3])
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run(["go", "go2"], k=[1,2,3], z=[1,2,3])

        # What about specifying sets of arguments together.
        # r = compile("write_dataset.cpp", OPTIMIZE="-O4").run("go", [dict(k=1, z=2), dict(k=2, z=3)])

        # alterante synax.  Seems worse because runner stuff is at the begining and the end.  compile is buried in the middle
        # r = CSE142Runner(MHz=[1000, 1100]).run(compile("write_dataset.cpp", OPTIMIZE="-O4").go, flush_caches=[True, False]), k=[1,2,3], z=[1,2,3]
        #
        # from LocalRunner import run as run_local
        # from MakeBuilder import build
        #
        # c = compile("write_dataset.cpp", OPTIMIZE="-O4")
        # r = run_local(c.go, flush_caches=[True, False]), k=[1,2,3], z=[1,2,3]

