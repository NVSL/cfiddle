import os
import pkg_resources
from .Toolchain import get_native_toolchain

PACKAGE_DATA_PATH = pkg_resources.resource_filename('cfiddle', 'resources/')

def cfiddle_lib_path():
    return os.path.join(PACKAGE_DATA_PATH, "libcfiddle", "build", get_native_toolchain())

def cfiddle_include_path():
    return os.path.join(PACKAGE_DATA_PATH, "include")

def print_cfiddle_lib_path():
    print(cfiddle_lib_path())

def print_cfiddle_include_path():
    print(cfiddle_include_path())

def setup_ld_path():

    if "LD_LIBRARY_PATH" in os.environ:
        ld_paths = os.environ["LD_LIBRARY_PATH"].split(":")
    else:
        ld_paths = []
    ld_paths.append(cfiddle_lib_path())
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
    return os.environ["LD_LIBRARY_PATH"]

def set_ld_path_in_shell():
    print(f"export LD_LIBRARY_PATH={setup_ld_path()}")
