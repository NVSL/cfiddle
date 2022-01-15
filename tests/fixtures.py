import pytest
from fiddle import *
from util import *
from fiddle.config import fiddle_config
import tempfile

@pytest.fixture
def setup():
    yield from _pristine_dir()

def _pristine_dir():
    with tempfile.TemporaryDirectory() as fiddle_dir:
        with fiddle_config(FIDDLE_BUILD_ROOT=fiddle_dir):
            yield fiddle_dir
            


@pytest.fixture
def test_cpp(setup):
    return build_one("test_src/test.cpp", verbose=True, rebuild=True)

