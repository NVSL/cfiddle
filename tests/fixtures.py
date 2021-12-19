import pytest
from fiddle import *

@pytest.fixture
def test_cpp():
    return build_one("test_src/test.cpp", verbose=True, rebuild=True)
