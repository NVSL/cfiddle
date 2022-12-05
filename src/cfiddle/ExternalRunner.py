import pickle
import click
import subprocess
import os
from .Runner import Runner
from .Exceptions import CFiddleException

class ExternalRunnerException(CFiddleException):
    pass

class BashExternalRunnerDelegate:
    def execute(self, command, runner):
        c = " ".join(command)
        os.system(f"""bash -c '{c}'""")

        
class SubprocessExternalRunnerDelegate:
    def execute(self, command, runner):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise ExternalRunnerException("ExternalRunner failed (error code {e.returncode}): {e.stdout} {e.stderr}")

  
class ExternalRunner(Runner):
    """Delegate running :class:`InvocationDescription` objects to an external process.
    
    This works by pickling this object, and invoking the :code:`cfiddle-run`
    command line tool to unpickle, run the invocations and then pickle
    the results.

    The :code:`cfiddle-run` command line is passed to
    :class:SubprocessExternalRunnerDelegate` which just runs it.  

    You can change this behavior by setting the
    :code:`ExternalCommandRunner_type` configuration option.  For
    instance, a replacement could submit the commandline to job
    scheduling system or execute it remotely via :code:`ssh`.

    """
    
    def run(self):
        from .config import get_config
        cmd_runner = get_config("ExternalCommandRunner_type")()

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
        

    def _pickle_run(self, f):
        from .config import peek_config
        with open(f, "wb") as r:
            pickle.dump(dict(config=peek_config(), runner=self), r)

    def _unpickle_results(self, f):
        with open(f, "rb") as r:
            return pickle.load(r)

    def _temp_files(self):
        from .config import get_config
        return os.path.join(get_config("CFIDDLE_BUILD_ROOT"), "runner.pickle"), os.path.join(get_config("CFIDDLE_BUILD_ROOT"), "results.pickle"), 


@click.command()
@click.option('--runner', "runner", required=True, type=click.File("rb"), help="File with a pickled Runner in it.")
@click.option('--results', "results", required=True, type=click.File("wb"), help="File to deposit the results in.")
def remote_runner(runner, results):
    do_remote_runner(runner, results)
    
def do_remote_runner(runner, results):
    from .config import cfiddle_config
    contents = pickle.load(runner)

    with cfiddle_config(**contents["config"]):
        try:
            return_value = super(ExternalRunner, contents["runner"]).run()
            pickle.dump(return_value, results)
        except CFiddleException as e:
            pickle.dump(e, results)

