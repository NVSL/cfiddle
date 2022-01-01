from fiddle import *
from fiddle.util import environment, invoke_process
from fiddle import PACKAGE_DATA_PATH, setup_ld_path, set_ld_path_in_shell, libfiddle_dir_path, print_libfiddle_dir
import os

def test_set_ld_path():
    with environment(LD_LIBRARY_PATH=None):
        assert "LD_LIBRARY_PATH" not in os.environ
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == os.path.join(PACKAGE_DATA_PATH, "libfiddle", "build")

    with environment(LD_LIBRARY_PATH="foo:bar"):
        setup_ld_path()
        assert os.environ["LD_LIBRARY_PATH"] == "foo:bar:" + os.path.join(PACKAGE_DATA_PATH, "libfiddle", "build")

def test_set_ld_path_in_shell():
    set_ld_path_in_shell()
    
def test_libfiddle_path():
    assert os.path.exists(os.path.join(libfiddle_dir_path(), "libfiddle.so"))
    print_libfiddle_dir()
    success, output = invoke_process(["fiddle-lib-path"])
    assert success
    assert os.path.exists(os.path.join(output.strip(), "libfiddle.so"))
    
