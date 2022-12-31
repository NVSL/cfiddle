import pytest
from cfiddle import *
from util import *
from cfiddle.config import cfiddle_config
import tempfile

@pytest.fixture
def setup():
    with cfiddle_config():
        enable_debug()
        yield from _pristine_dir()

        
def _pristine_dir():
    with tempfile.TemporaryDirectory() as cfiddle_dir:
        with cfiddle_config(CFIDDLE_BUILD_ROOT=cfiddle_dir):
            yield cfiddle_dir
            


@pytest.fixture
def test_cpp(setup):
    return build_one("test_src/test.cpp", verbose=True, rebuild=True)

