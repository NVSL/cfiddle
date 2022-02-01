from .GCC import GCCToolchain
from .Go import GoToolchain
from .Registry import ToolchainRegistry, TheToolchainRegistry
from .Exceptions import *

def list_architectures():
    """List available compilation-targets.

    Returns:
       `list of tuples`: Each tuple contains an architecture name and the corresponding toolchain prefix.
    """
    return list(GCCToolchain._gcc_architectures.items())



