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
        self._asm_function_bookends = self._asm_bookends 
        self._version, self._architecture_name = self._extract_version() # this will be wrong with we coss compile
        
    def get_target(self):
        success, value = invoke_process([self.get_compiler(), "-print-target-triple"])
        if not success:
            raise ToolError(f"Couldn't extract target name from {self.get_compiler()}")
        return value.strip()
        
    def get_tool(self, tool):
        if tool in ["c++filt", "llvm-cxxfilt"]:
            return f"llvm-cxxfilt-{self._version}"
        else:
            return f"llvm-{tool}-{self._version}"

    def _asm_bookends(self, function):
        return fr"^{re.escape(function)}:\s*", ".cfi_endproc"

    def _extract_version(self):
        success, output = invoke_process([self._compiler, "-v"])
        if not success:
            raise ToolError(f"Couldn't extract version from {self._compiler}.")
        lines = output.split("\n")
        
        m = re.search("version (\d+)\.\d+.\d+", lines[0])
        if not m:
            raise ToolError(f"Couldn't extract version from {self._compiler}.")
        version = m.group(1)
        
        m = re.match("Target: ([\w\-_]+)", lines[1])
        if not m:
            raise ToolError(f"Couldn't extract target from {self._compiler}.")
        target = m.group(1)
        return version, target
        
            
TheToolchainRegistry.register_toolchain(tool_regex=r"clang(\+\+)?(-\d+)?", languages=["C++", "C"], tc_type=ClangToolchain)

