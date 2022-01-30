from .util import get_native_architecture
import re

class Toolchain:
    pass
        
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

class GCCToolchain(Toolchain):
    def __init__(self):
        self._tool_prefix = ""
        
    def get_compiler_for_language(self, language):
        if language.upper() == "C":
            return f"{self._tool_prefix}gcc"
        if language.upper() == "C++":
            return f"{self._tool_prefix}g++"
    
class GCCX86(GCCToolchain):
    def __init__(self):
        self._tool_prefix = ""
    def get_asm_function_bookends(self, function):
        return (f"^{re.escape(function)}:\s*", ".cfi_endproc")

class GCCARM(GCCToolchain):
    def __init__(self):
        self._tool_prefix = "arm-linux-gnueabi-"

    def get_asm_function_bookends(self, function):
        return (f"^{re.escape(function)}:\s*", ".fnend")


class GoNative(Toolchain):
    
    def __init__(self):
        self._bintools_delegate = TheToolchainRegistry.get_toolchain(get_native_architecture(),
                                                                     "C")
        
    def get_asm_function_bookends(self, function):
        return self._bintools_delegate.get_asm_function_bookends()
    

TheToolchainRegistry.register_toolchain(architecture_names=["x86_64", "x86"], languages=["C++", "C"], tc_type=GCCX86)
TheToolchainRegistry.register_toolchain(architecture_names=["ARM"], languages=["C++", "C"], tc_type=GCCARM)

TheToolchainRegistry.register_toolchain(architecture_names=[get_native_architecture()], languages=["GO"], tc_type=GoNative)



