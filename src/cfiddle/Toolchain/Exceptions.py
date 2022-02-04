from ..Exceptions import CFiddleException

class ToolchainException(CFiddleException):
    pass

class ToolError(CFiddleException):
    pass

class UnknownToolchain(ToolchainException):
    pass
