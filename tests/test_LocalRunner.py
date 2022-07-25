from cfiddle import *
from util import *
from fixtures import *
from cfiddle.Runner import RunnerException

def test_hello_world(test_cpp):
    
    invocation = InvocationDescription(test_cpp, function="simple_print", arguments=dict(a=1, b=2, c=3))
    runner = LocalSingleRunner(invocation)
    invocation_result = runner.run()
    print(invocation_result.results)

def test_missing_function(test_cpp):
    invocation = InvocationDescription(test_cpp, function="missing", arguments=dict(a=1, b=2, c=3))
    with pytest.raises(RunnerException):
        runner = LocalSingleRunner(invocation).run()
    
