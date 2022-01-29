import pytest
from cfiddle import *
from cfiddle.util import get_native_arch, invoke_process
from fixtures import *

def check_architecture_skip(cross_arch):
    native_arch = get_native_arch()
    if cross_arch == native_arch:
        pytest.skip("Can't cross compile for {cross_arch} on {native_arch}.")

    success, _ = invoke_process([f"{cross_arch}-gcc","-v"])
    if not success:
        pytest.skip(f"{cross_arch} cross compiler is missing.")

def test_basic(setup):
    check_architecture_skip("arm-linux-gnueabi")
    print(build(code(r"""void foo(){}"""), arg_map(CXX="arm-linux-gnueabi-g++"))[0].asm())

def test_asm_extraction(setup):
    check_architecture_skip("arm-linux-gnueabi")
    print(build(code(r"""void foo(){}"""), arg_map(CXX="arm-linux-gnueabi-g++"))[0].asm("foo"))

def test_basic_ppc(setup):
    check_architecture_skip("powerpc-linux-gnu")
    print(build(code(r"""void foo(){}"""), arg_map(CXX="powerpc-linux-gnu-g++"))[0].asm())
