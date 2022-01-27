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
        assert isinstance(test_cpp, cfiddle.jupyter.source.FullyInstrumentedExecutable)
        assert isinstance(test_cpp.asm(), Code)
        assert isinstance(test_cpp.source(), Code)
        assert isinstance(test_cpp.preprocessed(), Code)
        assert isinstance(test_cpp.debug_info(), TextDisplayObject)
        assert isinstance(test_cpp.cfg("sum"), SVG)
        assert os.path.exists(os.path.join(test_cpp.build_dir, "sum.svg"))

def test_compare(setup):
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert isinstance(compare([test_cpp.cfg("sum"), test_cpp.cfg("sum")]), HTML)
    
