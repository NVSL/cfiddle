import re
import collections
import copy

from ..util import invoke_process

from .Toolchain import Toolchain
from .Registry import TheToolchainRegistry
from .Exceptions import *

class LinuxToolchain(Toolchain):

    def get_asm_function_bookends(self, function):
        return self._asm_function_bookends(function)

    def get_compiler(self):
        return self._compiler

    def describe(self):
        return f"{self._compiler} compiling for {self._architecture_name}"

    
class ClangToolchain(LinuxToolchain):

    def __init__(self, language, build_parameters):
        super().__init__(language, build_parameters)

        self._compiler = build_parameters.get("CC", build_parameters.get("CXX", "clang"))
        
        self._asm_function_bookends = lambda function: (fr"^{re.escape(function)}:\s*", ".cfi_endproc")

    def get_target(self):
        success, value = invoke_process([self.get_compiler(), "-print-target-triple"])
        if not success:
            raise ToolError(f"Couldn't extract target name from {self.get_compiler()}")
        return value.strip()
        
            
TheToolchainRegistry.register_toolchain(tool_regex=r"clang(\+\+)?", languages=["C++", "C"], tc_type=ClangToolchain)

