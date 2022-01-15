from cfiddle import *
from cfiddle.util import environment, invoke_process
from cfiddle import PACKAGE_DATA_PATH, setup_ld_path, set_ld_path_in_shell, libcfiddle_dir_path, print_libcfiddle_dir
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
    
def test_libcfiddle_path():
    assert os.path.exists(os.path.join(libcfiddle_dir_path(), "libcfiddle.so"))
    print_libcfiddle_dir()
    success, output = invoke_process(["cfiddle-lib-path"])
    assert success
    assert os.path.exists(os.path.join(output.strip(), "libcfiddle.so"))
    
