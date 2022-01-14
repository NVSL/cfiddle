import fiddle
import doctest
import pytest
from fixtures import *

# this just tests the doctests in the modules. Tests for the rest of the documentation is handled by the pytest command line.

@pytest.mark.parametrize("module", [fiddle.util])
def test_modules(module, setup):
    failures, tests = doctest.testmod(module, verbose=True)
    assert failures == 0
