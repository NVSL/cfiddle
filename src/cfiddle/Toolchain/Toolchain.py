import copy

from .Exceptions import ToolchainException
class Toolchain:

    def __init__(self, language, build_parameters):
        self._language = language.upper()
        self._build_parameters = copy.copy(build_parameters)

    def get_compiler_flags(self):
        return ""
    def get_linker_flags(self):
        return ""
