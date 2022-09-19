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
    
    This works by pickling this object, and invoking the `cfiddle-run`
    command line tool to unpickle, run the invocations and then pickle
    the results.

    The command line is passed to class specified is by the
    `ExternalCommandRunner_type` configuration option.  The default
    (:class:SubprocessExternalRunnerDelegate`) just runs it, but an
    alternate implementation could, e.g., use `ssh` to execute it
    remotely.
    """
    
    def run(self):
        from .config import get_config
        cmd_runner = get_config("ExternalCommandRunner_type")()

        runner_filename, results_filename = self._temp_files()

        self._pickle_self(runner_filename)


        cmd_runner.execute(["cfiddle-run", "--runner", runner_filename, "--results", results_filename], runner=self)

        r = self._unpickle_results(results_filename)
        if isinstance(r, Exception):
            raise r
        else:
            return r
        

    def _pickle_self(self, f):
        with open(f, "wb") as r:
            pickle.dump(self, r)

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
    t = pickle.load(runner)
    try:
        pickle.dump(super(ExternalRunner, t).run(), results)
    except CFiddleException as e:
        pickle.dump(e, results)
