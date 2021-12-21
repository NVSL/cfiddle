from fiddle import *
from fiddle.util import environment
from fiddle import PACKAGE_DATA_PATH, setup_ld_path, set_ld_path_in_shell
import os

def test_set_ld_path():
    with environment(LD_LIBRARY_PATH=None):
        assert "LD_LIBRARY_PATH" not in os.environ
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == os.path.join(PACKAGE_DATA_PATH, "libfiddle")

    with environment(LD_LIBRARY_PATH="foo:bar"):
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == "foo:bar:" + os.path.join(PACKAGE_DATA_PATH, "libfiddle")

def test_set_ld_path_in_shell():
    set_ld_path_in_shell()
    
