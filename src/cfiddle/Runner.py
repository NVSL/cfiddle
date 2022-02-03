from .Builder import Executable
from .Exceptions import CFiddleException
import collections
import os
from .util import type_check, type_check_list


class InvocationDescription:
    def __init__(self, executable, function, arguments, perf_counters=None):
        if perf_counters is None:
            perf_counters = []
        self.executable = executable
        self.function = function
        self.arguments = arguments
        self.perf_counters = perf_counters
        self._raise_on_invalid_types()

    def _raise_on_invalid_types(self):

        try:
            type_check(self.executable, Executable)
            type_check(self.function, str)
            type_check(self.arguments, dict)
            type_check_list(self.arguments.keys(), str)
        except (ValueError, TypeError) as e:
            raise InvalidInvocation(e)
            
class Runner:

    def __init__(self, invocation, result_factory=None):
        from .config import get_config
        self._invocation = invocation
        self._result_factory = result_factory or get_config("InvocationResult_type")

    
    def get_build_result(self):
        return self._invocation.executable

    
    def get_invocation(self):
        return self._invocation

    
    def run(self):
        raise NotImplemented
    

    def bind_arguments(self, arguments, signature):
        """
        Take mapping from parameter names to values a function signature and:
        1.  Check that the values of the arguments are compatible with the signature
        2.  Return an parameter list in the right order to call the function.
        """
        r = []
        for a in signature.parameters:
            if a.name not in arguments:
                raise MissingArgument(a.name)

            argument_value = arguments[a.name]

            try:
                ctype_value = a.type(argument_value)
            except TypeError as e:
                raise IncorrectArgumentType(f"Invalid value for argument '{a.name}' of function '{signature.name}'.  Expeted value compatible with '{a.type}' got '{argument_value}' (type '{type(argument_value)}'")

            r.append(ctype_value)

        for p in arguments:
            if not any(map(lambda x: x.name == p, signature.parameters)):
                raise UnusedArgument(p)
        return r

class InvocationResult:

    def __init__(self, invocation, results, return_value):
        self.invocation = invocation
        self.results = results
        self.return_value = return_value
        
    def get_results_field_names(self):
        if len(self.results) == 0:
            return []
        
        return self.results[0].keys()

    def get_results(self):
        return self.results
    

class RunnerException(CFiddleException):
    pass

class UnusedArgument(CFiddleException):
    pass

class MissingArgument(CFiddleException):
    pass

class IncorrectArgumentType(CFiddleException):
    pass

class InvalidInvocation(CFiddleException):
    pass
