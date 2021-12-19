from fiddle.MakeBuilder import MakeBuilder
from fiddle.LocalRunner import LocalRunner
from fiddle.Runner import InvocationDescription
from fiddle.Builder import ExecutableDescription

def test_hello_world():
    
    b = MakeBuilder(ExecutableDescription("test_src/test.cpp", build_parameters=dict(OPTIMIZE="-O0")))
    build_result = b.build()

    invocation = InvocationDescription(build_result, function="simple_print", arguments=dict(a=1, b=2, c=3))
    runner = LocalRunner(invocation)

    invocation_result = runner.run()
    
    print(invocation_result.results)
