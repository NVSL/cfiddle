
import pytest
from cfiddle import *
from cfiddle.util import get_native_arch, invoke_process

from fixtures import *

def check_skip():
    if "ARM" in get_native_arch().upper():
        pytest.skip("Can't cross compile for arm on arm")
    success, _ = invoke_process(["arm-linux-gnueabi-gcc"])
    if not success:
        pytest.skip("arm cross compiler is missing.")

def test_basic(setup):
    print(build(code(r"""void foo(){}"""), arg_map(CXX="arm-linux-gnueabi-g++"))[0].asm())

def test_asm_extraction(setup):
    print(build(code(r"""void foo(){}"""), arg_map(CXX="arm-linux-gnueabi-g++"))[0].asm("foo"))
