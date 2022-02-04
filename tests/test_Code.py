from cfiddle import *
from util import *
from cfiddle.config import get_config
import os

def test_code_cpp():
    build_and_run(code(r"""
    extern "C" 
        int four() {
    return 4;
    }
"""), {}, "four", {})
    assert os.path.exists(os.path.join(get_config("CFIDDLE_BUILD_ROOT"), "anonymous_code"))

def test_explicit_cpp():
    build_and_run(code(r"""
    extern "C" 
        int four() {
    return 4;
    }
""", language="c++"), {}, "four", {})


def test_code_c():
    build_and_run(code(r"""
    int four() {
        return 4;
    }
    """, language="c"), {}, "four", {})
