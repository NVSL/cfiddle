import pytest
from cfiddle import *
from cfiddle.util import  invoke_process
from cfiddle.Toolchain import get_native_toolchain, toolchain_present
from fixtures import *

@pytest.fixture
def simple_code():
    return code(r"""extern "C" void foo(){}""")


def skip_without_toolchain(cross_toolchain):
    if not toolchain_present(cross_toolchain):
        pytest.skip(f"{cross_toolchain} cross compiler is missing.")


@pytest.mark.parametrize("toolchain,arch,search",
                         [("arm-linux-gnueabi", "aarch64", "ldr"),
                          ("powerpc-linux-gnu", "ppc64", "stw"),
                          ("x86_64-linux-gnu", "x86_64", "rbp")])
def test_asm_extraction(setup, simple_code,
                        toolchain, arch, search):
    skip_without_toolchain(toolchain)
    asm = build(simple_code, arg_map(ARCH=arch, DEBUG_FLAGS=""), verbose=True)[0].asm("foo")
    print(asm)
    assert search in asm

def test_native(setup,simple_code):
    build(simple_code, arg_map(ARCH="native", DEBUG_FLAGS=""), verbose=True)
    
def test_multiarch(setup, simple_code):

    gcc_tool_chains = dict(aarch64 = "arm-linux-gnueabi", 
                           arm = "arm-linux-gnueabi", # include aliases
                           x86_64="x86_64-linux-gnu",
                           x86="x86_64-linux-gnu",
                           ppc64="powerpc-linux-gnu",
                           ppc="powerpc-linux-gnu",
                           native=get_native_toolchain())

    architectures = [x for (x,y) in gcc_tool_chains.items() if toolchain_present(y)]
    
    builds = build(simple_code, arg_map(ARCH=architectures, DEBUG_FLAGS=""), verbose=True)
    for b in builds:
        print(b.get_toolchain())
        print(b.get_toolchain().describe())
        print(b.asm())
        print(b.asm("foo"))

        
arm_toolchains = [x for x in ["g++-8", "g++-9", "g++-11"] if invoke_process([f"arm-linux-gnueabi-{x}", "-v"])[0]]


def test_naming(simple_code):
    skip_without_toolchain("arm-linux-gnueabi")
    b = build(simple_code, arg_map(ARCH=["arm", "aarch64"]))
    assert b[0].get_toolchain()._architecture_name == "aarch64".upper()
    assert b[1].get_toolchain()._architecture_name == "aarch64".upper()


def test_toolchain_spec_1(setup):
    skip_without_toolchain("arm-linux-gnueabi")
    sample = code(r"""extern "C" int answer() {return 42;}""")
    b = build(sample, arg_map(CXX=["g++", "arm-linux-gnueabi-g++"]))
    assert b[0].get_toolchain()._tool_prefix == ""
    assert b[1].get_toolchain()._tool_prefix == "arm-linux-gnueabi-"


    
def test_toolchain_spec_2(setup):
    skip_without_toolchain("arm-linux-gnueabi")
    sample = code(r"""extern "C" int answer() {return 42;}""")
    built = build(sample, arg_map(ARCH="aarch64", CXX=arm_toolchains), verbose=True)
    for i, b in enumerate(built):
        assert b.get_toolchain()._tool_prefix == "arm-linux-gnueabi-"
        assert b.get_toolchain()._compiler == f"arm-linux-gnueabi-{arm_toolchains[i]}"
