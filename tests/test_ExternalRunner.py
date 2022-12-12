from cfiddle import *
from fixtures import *
from cfiddle.ExternalRunner import ExternalRunner, BashExternalRunnerDelegate, SubprocessExternalRunnerDelegate
from cfiddle.config import enable_debug
from cfiddle.Runner import RunnerException


def test_external_runner_multi(test_cpp):
    with cfiddle_config(Runner_type=ExternalRunner):
        t = run(test_cpp, function=["sum", "product"], arguments=arg_map(a=[1,2], b=[3,4]))

    
def test_external_runner(setup):
    with cfiddle_config(Runner_type=ExternalRunner):
        assert sanity_test() == 4

    
def test_missing_function(test_cpp):

    with cfiddle_config(Runner_type=ExternalRunner):
        with pytest.raises(CFiddleException):
            run(executable=test_cpp, function="missing", arguments=dict(a=1, b=2, c=3))
            
        
@pytest.mark.parametrize("ExternalCommandRunner", [BashExternalRunnerDelegate,
                                                   SubprocessExternalRunnerDelegate])
def test_run_combo(test_cpp, ExternalCommandRunner):
    from test_full_flow import test_run_combo
    with cfiddle_config(Runner_type=ExternalRunner,
                        ExternalCommandRunner_type=ExternalCommandRunner):
        test_run_combo(test_cpp)

