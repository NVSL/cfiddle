import pytest
from cfiddle import *
from cfiddle.util import get_native_toolchain, invoke_process
from fixtures import *

@pytest.fixture
def simple_code():
    return code(r"""extern "C" void foo(){}""")


def skip_without_toolchain(cross_toolchain):
    if not tool_chain_present(cross_toolchain):
        pytest.skip(f"{cross_toolchain} cross compiler is missing.")

def tool_chain_present(cross_toolchain):
    success, _ = invoke_process([f"{cross_toolchain}-gcc","-v"])
    return success

@pytest.mark.parametrize("toolchain,arch,search",
                         [("arm-linux-gnueabi", "aarch64", "ldr"),
                          ("powerpc-linux-gnu", "ppc64", "stw"),
                          ("x86_64-linux-gnu", "x86_64", "rbp")])
def test_asm_extraction(setup, simple_code, toolchain, arch, search):
    skip_without_toolchain(toolchain)
    asm = build(simple_code, arg_map(ARCH=arch, DEBUG_FLAGS=""), verbose=True)[0].asm("foo")
    print(asm)
    assert search in asm

def test_native(setup,simple_code):
    build(simple_code, arg_map(ARCH="native", DEBUG_FLAGS=""), verbose=True)
    
def test_multiarch(setup, simple_code):

    gcc_tool_chains = dict(aarch64 = "arm-linux-gnueabi", 
                           arm = "arm-linux-gnueabi", # include aliases
                           x86_64="x86_64-linux-gnu-gcc",
                           x86="x86_64-linux-gnu-gcc",
                           ppc64="powerpc-linux-gnu",
                           ppc="powerpc-linux-gnu",
                           native=get_native_toolchain())

    architectures = [x for (x,y) in gcc_tool_chains.items() if tool_chain_present(y)]
    
    builds = build(simple_code, arg_map(ARCH=architectures, DEBUG_FLAGS=""), verbose=True)
    for b in builds:
        print(b.get_toolchain())
        print(b.asm("foo"))
        print(b.describe())


