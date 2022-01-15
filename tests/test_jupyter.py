from fiddle import *
from util import *
from fixtures import *
from fiddle.jupyter import *
from fiddle.jupyter.util import *
import fiddle.jupyter.source
import IPython
from fiddle.config import fiddle_config
from IPython.display import SVG, HTML
import os

def test_jupyter(setup):
    with fiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert isinstance(test_cpp, fiddle.jupyter.source.FullyInstrumentedExecutable)
        assert isinstance(test_cpp.asm(), IPython.display.Code)
        assert isinstance(test_cpp.source(), IPython.display.Code)
        assert isinstance(test_cpp.preprocessed(), IPython.display.Code)
        assert isinstance(test_cpp.cfg("sum"), SVG)
        assert os.path.exists(os.path.join(test_cpp.build_dir, "sum.svg"))

def test_compare(setup):
    with fiddle_config():
        configure_for_jupyter()
        test_cpp = build_one("test_src/test.cpp")
        assert isinstance(compare([test_cpp.cfg("sum"), test_cpp.cfg("sum")]), HTML)
    
