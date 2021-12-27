from fiddle import *
from util import *
from fixtures import *

def test_hello_world(test_cpp):
    
    invocation = InvocationDescription(test_cpp, function="simple_print", arguments=dict(a=1, b=2, c=3))
    runner = LocalRunner(invocation)
    invocation_result = runner.run()
    print(invocation_result.results)

def test_missing_function(test_cpp):
    invocation = InvocationDescription(test_cpp, function="missing", arguments=dict(a=1, b=2, c=3))
    with pytest.raises(UnknownSymbol):
        runner = LocalRunner(invocation).run()
    
