from cfiddle import *
from util import *
from fixtures import *
from cfiddle.source import FullyInstrumentedExecutable
from cfiddle.util import working_directory
import pytest
import tempfile
import os


def test_cfg(test_cpp):
    
    assert isinstance(test_cpp, FullyInstrumentedExecutable)

    with tempfile.TemporaryDirectory() as d:
        png = os.path.join(d, "test.png")
        svg = os.path.join(d, "test.svg")
        test_cpp.cfg("four", output=png)
        assert os.path.exists(png)
        test_cpp.cfg("four", svg)
        assert os.path.exists(svg)

