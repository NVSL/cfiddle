from cfiddle import *
from cfiddle.util import environment, invoke_process
from cfiddle.paths import *
import os

def test_set_ld_path():
    with environment(LD_LIBRARY_PATH=None):
        assert "LD_LIBRARY_PATH" not in os.environ
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == os.path.join(PACKAGE_DATA_PATH, "libcfiddle", "build")

    with environment(LD_LIBRARY_PATH="foo:bar"):
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == "foo:bar:" + os.path.join(PACKAGE_DATA_PATH, "libcfiddle", "build")

def test_set_ld_path_in_shell():
    set_ld_path_in_shell()
    
def test_cfiddle_paths(): 
    assert os.path.exists(os.path.join(cfiddle_lib_path(), "libcfiddle.so"))
    print_cfiddle_lib_path()
