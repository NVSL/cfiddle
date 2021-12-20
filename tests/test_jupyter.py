from fiddle import *
from fiddle.jupyter import *
import fiddle.jupyter.source
import IPython

def test_jupyter():
    configure_for_jupyter()

    r = build_one("test_src/test.cpp")
    assert isinstance(r, fiddle.jupyter.source.FullyInstrumentedExecutable)
    assert isinstance(r.asm(), IPython.display.Code)
