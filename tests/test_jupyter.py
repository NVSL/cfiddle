from cfiddle import *
from util import *
from fixtures import *
from cfiddle.jupyter import *
from cfiddle.jupyter.util import *
import cfiddle.jupyter.source
import IPython
from cfiddle.config import cfiddle_config
from IPython.display import SVG, HTML, TextDisplayObject, Code
import os

def test_jupyter(setup):
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert isinstance(test_cpp, cfiddle.jupyter.source.InstrumentedExecutable)
        assert isinstance(test_cpp.asm(), Code)
        assert isinstance(test_cpp.source(), Code)
        assert isinstance(test_cpp.preprocessed(), Code)
        assert isinstance(test_cpp.debug_info(), str)
        assert isinstance(test_cpp.cfg("sum"), SVG)
        assert os.path.exists(os.path.join(test_cpp.build_dir, "sum.svg"))

def test_raw_output_in_jupyter(setup):
    test_cpp_outside = build_one("test_src/test.cpp")
    
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert test_cpp.raw_preprocessed() == test_cpp_outside.preprocessed()
        assert test_cpp.raw_asm() == test_cpp_outside.asm()
        assert test_cpp.raw_source() == test_cpp_outside.source()
        

def test_compare(setup):
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert isinstance(compare([test_cpp.cfg("sum"), test_cpp.cfg("sum"), "AOEU"]), HTML)
    
