from cfiddle import Toolchain
from cfiddle import *
from cfiddle.Toolchain import GCCToolchain, GoToolchain, ToolchainException, UnknownToolchain
from cfiddle.util import get_native_architecture
import pytest


@pytest.mark.parametrize("lang,parameters,tool,toolchain",
                         [("c++", dict(ARCH="x86_64"), "g++", GCCToolchain),
                          ("c", dict(ARCH="x86_64"), "gcc", GCCToolchain),
                          ("c", dict(ARCH="X86_64"), "gcc", GCCToolchain),
                          ("c", {}, "gcc", GCCToolchain),
                          ("c", {}, "arm-linux-gnueabi-gcc", GCCToolchain),
                          ("C", {}, "gcc", GCCToolchain),
                          ("c++", dict(CXX="x86_64-linux-gnu-g++"), "g++", GCCToolchain),
                          ("go", {}, "go", GoToolchain),
                         ])
def test_resolve(lang, parameters, tool, toolchain):
    assert isinstance(Toolchain.TheToolchainRegistry.get_toolchain(lang,parameters, tool), toolchain)

@pytest.mark.parametrize("lang,parameters",
                         [("C",dict(ARCH="aoeu")),
                          ("C", dict(ARCH="arm", CC="arm-linux-gnueabi-gcc"))])
def test_unknown(lang, parameters):
    with pytest.raises(ToolchainException):
        Toolchain.TheToolchainRegistry.get_toolchain(lang,parameters, "gcc")
        
@pytest.mark.parametrize("parameters,basetool,tool,result",
                         [(dict(), "g++", "c++filt", "c++filt"),
                          (dict(ARCH="arm"), "g++", "c++filt", "arm-linux-gnueabi-c++filt")])
def test_tool(parameters,basetool,tool,result):
    assert Toolchain.TheToolchainRegistry.get_toolchain("C++", parameters,basetool).get_tool(tool) == result

def test_gcc_toolchain():
    for a in GCCToolchain._gcc_architectures:
        Toolchain.TheToolchainRegistry.get_toolchain("C", dict(ARCH=a), "gcc").describe()
        Toolchain.TheToolchainRegistry.get_toolchain("C", dict(ARCH=a), "gcc").get_asm_function_bookends("foo")

def test_unknown_toolchain():
    
    with pytest.raises(UnknownToolchain):
        build(code(r"""extern "C" void foo(){}"""), arg_map(CXX="aoeu"))
     
@pytest.mark.parametrize("language,build_parameters,prefix,gcc_tool,gpp_tool",
                         [("C", dict(ARCH="ppc"), "powerpc-linux-gnu-", "gcc", None),
                          ("C",  dict(CC="powerpc-linux-gnu-gcc"), "powerpc-linux-gnu-", "gcc", None),
                          ("C++", dict(CXX="powerpc-linux-gnu-g++"), "powerpc-linux-gnu-", None, "g++"),
                          ("C", dict(ARCH="ppc", CC="gcc-9"), "powerpc-linux-gnu-", "gcc-9", None),
                          ("C", dict(CC="powerpc-linux-gnu-gcc-9"), "powerpc-linux-gnu-", "gcc-9", None),
                          ("C", dict(CC="gcc-9"), "", "gcc-9", None),
                          ("C", dict(CC="gcc"), "", "gcc", None),
                          ("C", {}, "", "gcc", None),
                          ("C++", dict(CXX="powerpc-linux-gnu-g++-9"), "powerpc-linux-gnu-", None, "g++-9"),
                         ])
def test_GCC(language, build_parameters, prefix, gcc_tool, gpp_tool):
        
    if "ppc" in get_native_architecture():
        pytest.skip("This assumes ppc is not the native toolchain")

    if language == "C":
        tool = build_parameters.get("CC", "gcc")
    elif language == "C++":
        tool = build_parameters.get("CXX", "g++")

    tool_chain = Toolchain.TheToolchainRegistry.get_toolchain(language, build_parameters, tool)
    assert isinstance(tool_chain, GCCToolchain)
    assert tool_chain._tool_prefix == prefix
    if gcc_tool:
        assert tool_chain._compiler_suffix == gcc_tool
    if gpp_tool:
        assert tool_chain._compiler_suffix == gpp_tool
