from .Toolchain import Toolchain
from .Registry import TheToolchainRegistry

class GoToolchain(Toolchain):

    # Go cross compilation: https://stackoverflow.com/questions/32557438/how-do-i-cross-compile-my-go-program-from-mac-os-x-to-ubuntu-64-bit
    # and here https://stackoverflow.com/questions/23377271/how-do-i-cross-compile-a-go-program-on-a-mac-for-ubuntu
    # and here https://dave.cheney.net/2015/03/03/cross-compilation-just-got-a-whole-lot-better-in-go-1-5
    def __init__(self, language, build_parameters):
        self._bintools_delegate = TheToolchainRegistry.get_toolchain("C", build_parameters, "gcc")
        
    def get_asm_function_bookends(self, function):
        return self._bintools_delegate.get_asm_function_bookends(function)

    def get_compiler(self):
        return "go"

    def get_target(self):
        return self._bintools_delegate.get_target()
    
    def describe(self):
        return f"Go toolchain compiling for NATIVE"
    
TheToolchainRegistry.register_toolchain(tool_regex=r"go", languages=["GO"], tc_type=GoToolchain)

