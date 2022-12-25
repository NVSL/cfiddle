from ..util import invoke_process

from .GCC import GCCToolchain
from .Go import GoToolchain
from .Clang import ClangToolchain
from .Registry import ToolchainRegistry, TheToolchainRegistry
from .Exceptions import *

def list_architectures():
    """List available compilation-targets.

    Returns:
       `list of tuples`: Each tuple contains an architecture name and the corresponding toolchain prefix.
    """
    return list(GCCToolchain._gcc_architectures.items())


def get_native_toolchain():
    success, arch = invoke_process(["gcc", "-print-multiarch"])
    if not success:
        raise ToolchainException("Unable to determine native toolchain.")
    return arch.strip()

def toolchain_present(cross_toolchain):
    success, _ = invoke_process([f"{cross_toolchain}-gcc","-v"])
    return success
