from .util import get_native_architecture
import re
        
class ToolchainRegistry:
    def __init__(self):
        self._toolchains = {}
        self._native_architecture = get_native_architecture()
        
    def register_toolchain(self, architecture_names, languages, tc_type):
        for a in architecture_names:
            for l in languages:
                self._toolchains[(a.upper(), l.upper())] = tc_type

    def get_toolchain(self, architecture, language):

        if architecture.upper() == "NATIVE":
            architecture = self._native_architecture
            
        key = (architecture.upper(), language.upper())
        if key not in self._toolchains:
            print("\n".join(map(str,self.get_available_toolchains())))
            raise UnknownToolchain(f"No toolchain is available for {language} on {architecture}.")
        else:
            return self._toolchains[key]

    def get_available_toolchains(self):
        return self._toolchains.keys()

TheToolchainRegistry = ToolchainRegistry()    


class UnknownToolchain(Exception):
    pass


class Toolchain:
    pass


class GCCToolchain(Toolchain):
    def __init__(self):
        self._tool_prefix = ""
        
    def get_compiler_for_language(self, language):
        if language.upper() == "C":
            return f"{self._tool_prefix}gcc"
        if language.upper() == "C++":
            return f"{self._tool_prefix}g++"

    def update_suffix_for_native(self):
        if self.architecture_name == get_native_architecture():
            self._tool_prefix = ""

    def get_asm_function_bookends(self, function):
        return (f"^{re.escape(function)}:\s*", ".cfi_endproc")

    def get_tool(self, tool):
        return f"{self._tool_prefix}{tool}"

    
class GCC_X86_64(GCCToolchain):

    def __init__(self):
        self.architecture_name = "x86_64" # value returned by os.uname().machine
        self._tool_prefix = "x86_64-linux-gnu-"
        self.update_suffix_for_native()
        

class GCC_ARM_64(GCCToolchain):
    def __init__(self):
        self.architecture_name = "aarch64" # value returned by os.uname().machine
        self._tool_prefix = "arm-linux-gnueabi-"
        self.update_suffix_for_native()
        
    def get_asm_function_bookends(self, function):
        return (f"^{re.escape(function)}:\s*", ".fnend")

    
class GCC_PowerPC_64(GCCToolchain):
    def __init__(self):
        self._tool_prefix = "powerpc-linux-gnu-"
        self.architecture_name = "ppc64" # value returned by os.uname().machine.
        # a guess based on https://stackoverflow.com/questions/45125516/possible-values-for-uname-m  I don't have ppc machine
        self.update_suffix_for_native()



class Go_Native(Toolchain):

    # Go cross compilation: https://stackoverflow.com/questions/32557438/how-do-i-cross-compile-my-go-program-from-mac-os-x-to-ubuntu-64-bit
    # and here https://stackoverflow.com/questions/23377271/how-do-i-cross-compile-a-go-program-on-a-mac-for-ubuntu
    # and here https://dave.cheney.net/2015/03/03/cross-compilation-just-got-a-whole-lot-better-in-go-1-5
    def __init__(self):
        self._bintools_delegate = TheToolchainRegistry.get_toolchain(get_native_architecture(), "C")
        
    def get_asm_function_bookends(self, function):
        return self._bintools_delegate.get_asm_function_bookends()
    

TheToolchainRegistry.register_toolchain(architecture_names=["x86_64","x86"], languages=["C++", "C"], tc_type=GCC_X86_64)
TheToolchainRegistry.register_toolchain(architecture_names=["aarch64","arm"], languages=["C++", "C"], tc_type=GCC_ARM_64)
TheToolchainRegistry.register_toolchain(architecture_names=["ppc64", "ppc"], languages=["C++", "C"], tc_type=GCC_PowerPC_64)
TheToolchainRegistry.register_toolchain(architecture_names=[get_native_architecture()], languages=["GO"], tc_type=Go_Native)



