import os
import pkg_resources

def setup_ld_path():
    PACKAGE_DATA_PATH = pkg_resources.resource_filename('fiddle', 'resources/')
    ld_paths = os.environ["LD_LIBRARY_PATH"].split(":");
    ld_paths += os.path.join(PACKAGE_DATA_PATH, "libfiddle")
    os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths)
