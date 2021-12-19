import collections
import os

Runnable = collections.namedtuple("Runnable", "function,arguments")

Invocation = collections.namedtuple("Invocation", "executable,invocation_spec")

class Runner:

    def __init__(self, invocation, result_factory=None):
        self._invocation = invocation
        self._result_factory = result_factory or InvocationResult

    
    def get_runnable(self):
        return self._invocation.invocation_spec

    
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
            r.append(a.type(arguments[a.name]))

        for p in arguments:
            if not any(map(lambda x: x.name == p, signature.parameters)):
                raise UnusedArgument(p)
        return r


class InvocationResult:

    def __init__(self, invocation, results):
        self.invocation = invocation
        self.results = results

    def get_results_field_names(self):
        return self.results[0].keys()

    def get_results(self):
        return self.results
        


class UnusedArgument(Exception):
    pass

class MissingArgument(Exception):
    pass


