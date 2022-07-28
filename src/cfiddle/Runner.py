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
    """Runs a set of invocations.

    This encapsulates the conversion from
    :class:`InvocationDescription` to :class:`InvocationResults`.
    This is default implementation uses :class:`LocalSingleRunner` to
    perform each execution.  An alterante class can bespecified via
    the `SingleRunner_type` configuration option.

    Creating a subclass allows for other execution methods.  Notably,
    :class:`ExternalRunner` allows for execution via an external
    process.

    """

    def __init__(self, invocations,
                 single_runner=None,
                 result_factory=None,
                 result_list_factory=None,
                 progress_bar=None):
        from .config import get_config
        self._invocations = invocations
        self._single_runner = single_runner or get_config("SingleRunner_type")
        self._result_factory = result_factory or get_config("InvocationResult_type")
        self._result_list_factory = result_list_factory or get_config("InvocationResultsList_type")
        self._progress_bar = progress_bar or get_config("ProgressBar")


    def run(self):
        """
        Run our :class:`InvocationDescription`s, return a list of :class:`InvocationResult`.
        """
        
        return self._do_run(self._invocations)
    
    def _do_run(self, invocations):
        l = self._result_list_factory()
        for i in self._progress_bar(invocations, miniters=1):
            l.append(self._single_runner(i, self._result_factory).run())
        return l

    
    @classmethod
    def bind_arguments(cls, arguments, signature):
        """
        Take mapping from parameter names to values a function signature and:
        1.  Check that the values of the arguments are compatible with the signature
        2.  Return a parameter list in the right order to call the function.
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
