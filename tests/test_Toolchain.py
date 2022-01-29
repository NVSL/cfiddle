from cfiddle import Toolchain
from cfiddle.Toolchain import X86, ARM, UnknownToolchain
from cfiddle.util import get_native_architecture
import pytest

@pytest.mark.parametrize("arch,lang,toolchain",
                         [("x86", "c++", X86),
                          ("x86_64", "C", X86),
                          ("ARM", "c++", ARM),
                         ])
def test_resolve(arch, lang, toolchain):
    assert Toolchain.TheToolchainRegistry.get_toolchain(arch, lang) == toolchain

def test_native():
    assert Toolchain.TheToolchainRegistry.get_toolchain("native", "C++") == Toolchain.TheToolchainRegistry.get_toolchain(get_native_architecture(), "C++")

def test_failure():
    with pytest.raises(UnknownToolchain):
        Toolchain.TheToolchainRegistry.get_toolchain("foo", "bar")
