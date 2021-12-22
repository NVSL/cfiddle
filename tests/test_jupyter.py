from fiddle import *
from fiddle.jupyter import *
import fiddle.jupyter.source
import IPython
from fiddle.config import fiddle_config

def test_jupyter():
    with fiddle_config():
        configure_for_jupyter()

        r = build_one("test_src/test.cpp")
        assert isinstance(r, fiddle.jupyter.source.FullyInstrumentedExecutable)
        assert isinstance(r.asm(), IPython.display.Code)
        assert isinstance(r.source(), IPython.display.Code)
        assert isinstance(r.preprocessed(), IPython.display.Code)
