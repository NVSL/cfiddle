from cfiddle import *
from fixtures import *

def test_compile(setup):
    b = build(code(r"""extern "C" void foo(){}"""), arg_map(CXX="clang++"))
    assert b[0].get_toolchain().get_compiler() == "clang++"
    
def test_run(setup):
    run(build(code(r"""extern "C" void foo(){}"""), arg_map(CXX="clang++")), "foo")

def test_c(setup):
    source = code(r"""void foo(){}""", language="c")
    b = build(source, arg_map(CC="clang"), verbose=True)
    run(b, "foo")
    assert b[0].build_spec.get_language() == "c"
    assert b[0].get_toolchain().get_compiler() == "clang"

def test_c(setup):
    source = code(r"""void foo(){}""", language="c")
    b = build(source, arg_map(CC="clang"), verbose=True)
    run(b, "foo")
    assert b[0].build_spec.get_language() == "c"
    assert b[0].get_toolchain().get_compiler() == "clang"

def test_versions(setup):
    source = code(r"""void foo(){}""", language="c")
    b = build(source, arg_map(CC=["clang", "clang-10"]), verbose=True)
    run(b, "foo")
    assert b[0].get_toolchain().get_compiler() == "clang"
    assert b[1].get_toolchain().get_compiler() == "clang-10"

def test_tools(setup):
    source = code(r"""void foo(){}""", language="c")
    built = build(source, arg_map(CC=["clang", "clang-10"]), verbose=True)
    for b in built:
        assert b.get_toolchain().get_tool("c++filt") == "llvm-cxxfilt-10"
        assert b.get_toolchain().get_tool("objdump") == "llvm-objdump-10"
        

def test_describe(setup):
    source = code(r"""void foo(){}""", language="c")
    built = build(source, arg_map(CC=["clang"]), verbose=True)
    built[0].get_toolchain().describe()
    
def test_maps_experiment(setup):

    executables = [MakeBuilder(ExecutableDescription("test_src/std_maps.cpp", build_parameters=p), verbose=True, rebuild=True).build()
                               for p in arg_map(OPTIMIZE=["-O0", "-O3"])]

    invocations = [InvocationDescription(**i) for i in arg_map(executable=executables, function=["ordered", "unordered"], arguments=arg_map(count=map(lambda x: 2**x, range(0,10))))]

    results = InvocationResultsList(LocalRunner(i).run() for i in invocations)
    
    print(results.as_df())
    return results.as_df()

