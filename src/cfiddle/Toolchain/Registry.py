import re
from .Exceptions import UnknownToolchain

class ToolchainRegistry:
    def __init__(self):
        self._toolchains = []
        
    def register_toolchain(self, tool_regex, languages, tc_type):
        self._toolchains.append((tool_regex, list(map(lambda x: x.upper(), languages)), tc_type))

    def get_toolchain(self, language, build_parameters, tool):

        for pattern, languages, tc_type  in self._toolchains:
            if re.match(pattern, tool):
                if language.upper() in languages:
                    return tc_type(language, build_parameters)

        raise UnknownToolchain(f"Toolchain for '{tool}' is not recognized.")

TheToolchainRegistry = ToolchainRegistry()    

