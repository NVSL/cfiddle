import pytest
from cfiddle import *
from cfiddle.util import get_native_toolchain, invoke_process
from fixtures import *
@pytest.fixture
def simple_code():
    return code(r"""extern "C" void foo(){}""")


def check_for_toolchain(cross_toolchain):
    success, _ = invoke_process([f"{cross_toolchain}-gcc","-v"])
    if not success:
        pytest.skip(f"{cross_toolchain} cross compiler is missing.")

def test_basic(setup, simple_code):
    check_for_toolchain("arm-linux-gnueabi")
    print(build(simple_code, arg_map(CXX="arm-linux-gnueabi-g++"))[0].asm())

    
def test_asm_extraction(setup, simple_code):
    check_for_toolchain("arm-linux-gnueabi")
    print(build(simple_code, arg_map(ARCH="ARM"))[0].asm("foo"))

def test_basic_ppc(setup, simple_code):
    check_for_toolchain("powerpc-linux-gnu")
    print(build(simple_code, arg_map(CXX="powerpc-linux-gnu-g++"))[0].asm())

def test_multiarch_by_arch(setup, simple_code):
    check_for_toolchain("arm-linux-gnueabi")
    b = build(simple_code, arg_map(ARCH=["ARM", "x86"], DEBUG_FLAGS=""), verbose=True)
    print(b[0].get_toolchain())
    print(b[0].asm("foo"))
    print(b[1].get_toolchain())
    print(b[1].asm("foo"))
    assert "rbp" not in b[0].asm("foo")
    assert "rbp" in b[1].asm("foo")
        
def test_multiarch_by_tool(setup, simple_code):
    check_for_toolchain("arm-linux-gnueabi")
    b = build(simple_code, arg_map(CXX=["arm-linux-gnueabi-g++", "g++"]))
    assert "rbp" not in b[0].asm("foo")
    assert "rbp" in b[1].asm("foo")


