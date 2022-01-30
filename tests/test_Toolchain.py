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

@pytest.mark.parametrize("arch,tool,result",
                         [("native", "c++filt", "c++filt"),
                          ("arm", "c++filt", "arm-linux-gnueabi-c++filt")])
def test_tool(arch, tool,result):
    assert Toolchain.TheToolchainRegistry.get_toolchain(arch, "C++")().get_tool(tool) == result
    
def test_list():
    from cfiddle import list_toolchains
    list_toolchains()
    Toolchain.list_toolchains()


def test_toolchain():
    for t in Toolchain.list_toolchains():
        Toolchain.TheToolchainRegistry.get_toolchain(*t)().describe()
        Toolchain.TheToolchainRegistry.get_toolchain(*t)().get_asm_function_bookends("foo")
