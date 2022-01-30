from cfiddle import Toolchain
from cfiddle.Toolchain import GCC_X86_64, GCC_ARM_64, UnknownToolchain
from cfiddle.util import get_native_architecture
import pytest

@pytest.mark.parametrize("arch,lang,toolchain",
                         [("x86", "c++", GCC_X86_64),
                          ("x86_64", "C", GCC_X86_64),
                          ("ARM", "c++", GCC_ARM_64),
                         ])
def test_resolve(arch, lang, toolchain):
    assert Toolchain.TheToolchainRegistry.get_toolchain(arch, lang) == toolchain

def test_native():
    assert Toolchain.TheToolchainRegistry.get_toolchain("native", "C++") == Toolchain.TheToolchainRegistry.get_toolchain(get_native_architecture(), "C++")

def test_failure():
    with pytest.raises(UnknownToolchain):
        Toolchain.TheToolchainRegistry.get_toolchain("foo", "bar")
