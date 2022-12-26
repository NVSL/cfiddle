import copy
import os
import pickle
import click
import subprocess
import uuid

from .Builder import Executable
from .Exceptions import CFiddleException
from .util import type_check, type_check_list

class InvocationDescription:
    def __init__(self, executable, function, arguments, perf_counters=None, run_options=None):
        if perf_counters is None:
            perf_counters = []
        if run_options is None:
            run_options = dict()

        self.executable = executable
        self.function = function
        self.arguments = arguments
        self.perf_counters = perf_counters
        self.run_options = run_options
        self._raise_on_invalid_types()

    def _raise_on_invalid_types(self):

        try:
            type_check(self.executable, Executable)
            type_check(self.function, str)
            type_check(self.arguments, dict)
            type_check_list(self.arguments.keys(), str)
            type_check_list(self.perf_counters, str)
        except (ValueError, TypeError) as e:
            raise InvalidInvocation(e)

        
class RunOptionInterpreter(object):
    """

    Interpret the contents of the  :code:`run_options` argument to :func:`cfiddle.run`.

    This is a context manager.  The base class implementation just copies the values into environment variables.  Subclasses or substitutions could implement other behavior.
    
    """
    
    def __init__(self, options):
        self._options = options

    def apply_options(self):
        self._old_env = copy.deepcopy(os.environ)
        os.environ.update(self._stringize(self._options))
        
    def revert_options(self):
        os.environ.clear()
        os.environ.update(self._old_env)
        
    def __enter__(self):
        self.apply_options()

    def __exit__(self, type, value, traceback):
        self.revert_options()

    def _stringize(self, m):
            return {str(k):str(v) for k,v in m.items()}
        
class Runner:
    """

    Runs a set of :class:`InvocationDescription` instances to produce
    to :class:`InvocationResults`.  

    Execution occurs in a separate process to protect the python
    interpreter from misbehaving functions (e.g., segmentation
    faults).  

    This works by pickling this object, and invoking the
    :code:`cfiddle-run` command line tool to unpickle this object, run the
    invocations, and then pickle and return the results.

    The :code:`cfiddle-run` command line is passed to
    :class:SubprocessDelegate` which runs with Python's 
    :func:`subprocess.run()`.

    You can change this behavior by setting the
    :code:`RunnerDelegate_type` configuration option.  For
    instance, a replacement could submit the commandline to job
    scheduling system or execute it remotely via :code:`ssh`.

    Creating a subclass allows for other execution methods.  Notably,
    :class:`DirectRunner` runs the function in the current Python
    process, which can be useful in some instances.
    
    """

    def __init__(self, invocations,
                 invoker=None,
                 result_factory=None,
                 result_list_factory=None,
                 progress_bar=None):
        from .config import get_config
        self._invocations = invocations
        self._invoker = invoker or get_config("Invoker_type")
        self._result_factory = result_factory or get_config("InvocationResult_type")
        self._result_list_factory = result_list_factory or get_config("InvocationResultsList_type")
        self._progress_bar = progress_bar or get_config("ProgressBar")
        self._cmd_runner = get_config("RunnerDelegate_type")
        self._uuid = get_uuid()


    def run(self):
        cmd_runner = self._cmd_runner()
        
        runner_filename, results_filename = self._temp_files()
        if os.path.exists(results_filename):
            os.remove(results_filename)

        self._pickle_run(runner_filename)

        cmd_runner.execute(["cfiddle-run", "--runner", runner_filename, "--results", results_filename], runner=self)

        r = self._unpickle_results(results_filename)
        if isinstance(r, Exception):
            raise r
        else:
            return r
        
    def _delegated_run(self):
        l = self._result_list_factory()
        for i in self._progress_bar(self._invocations, miniters=1):
            l.append(self._invoker(i, self._result_factory).run())
        return l
    
    def get_invocations(self):
        return self._invocations

    def _pickle_run(self, f):
        from .config import peek_config
        with open(f, "wb") as r:
            pickle.dump(dict(config=peek_config(), runner=self), r)

    def _unpickle_results(self, f):
        with open(f, "rb") as r:
            return pickle.load(r)

    def _temp_files(self):
        from .config import get_config
        os.makedirs(os.path.join(get_config("CFIDDLE_BUILD_ROOT"), self._uuid))
        return os.path.join(get_config("CFIDDLE_BUILD_ROOT"), self._uuid, "runner.pickle"), os.path.join(get_config("CFIDDLE_BUILD_ROOT"), self._uuid, "results.pickle")

    
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
                raise MissingArgument(f"Argument '{a.name}' is missing for invocation of function '{signature.name}'.")

            argument_value = arguments[a.name]

            try:
                ctype_value = a.type(argument_value)
            except TypeError as e:
                raise IncorrectArgumentType(f"Invalid value for argument '{a.name}' of function '{signature.name}'.  Expeted value compatible with '{a.type}' got '{argument_value}' (type '{type(argument_value)}'")

            r.append(ctype_value)

        for p in arguments:
            if not any(map(lambda x: x.name == p, signature.parameters)):
                raise UnusedArgument(f"Argument '{p}' was provided but is not the signature of function '{signature.name}'.")
        return r

class DirectRunner(Runner):
    """
    Run code in the current Python process instead of a separate process.

    You can use it like so:

    .. doctest::

        >>> from cfiddle import  *
        >>> sample = code(r'''
        ... #include <cfiddle.hpp>
        ... extern "C"
        ... int loop(int count) {
        ...	   int sum = 0;
        ...    for(int i = 0; i < count; i++) {
        ...       sum += i;
        ...    }
        ...    return sum;
        ... }
        ... ''')
        >>> exes = build(sample)
        >>> with cfiddle_config(Runner_type=DirectRunner):
        ...    results = run(exes, "loop", arguments=arg_map(count=[1]))

    """
    
    def run(self):
        return self._delegated_run()


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
    

class BashDelegate:
    def execute(self, command, runner):
        c = " ".join(command)
        os.system(f"""bash -c '{c}'""")

        
class SubprocessDelegate:
    def execute(self, command, runner):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RunnerDelegateException(f"SubprocessDelegate failed (error code {e.returncode}): {e.stdout} {e.stderr}")

def get_uuid(id_length=8):
    return uuid.uuid4().hex[:id_length]

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

class InvalidRunOption(CFiddleException):
    pass

class RunnerDelegateException(CFiddleException):
    pass

@click.command()
@click.option('--runner', "runner", required=True, type=click.File("rb"), help="File with a pickled Runner in it.")
@click.option('--results', "results", required=True, type=click.File("wb"), help="File to deposit the results in.")
def invoke_runner(runner, results):
    do_invoke_runner(runner, results)
    
def do_invoke_runner(runner, results):
    from .config import cfiddle_config
    contents = pickle.load(runner)

    with cfiddle_config(**contents["config"]):
        try:
            return_value = contents["runner"]._delegated_run()
            pickle.dump(return_value, results)
        except CFiddleException as e:
            pickle.dump(e, results)

