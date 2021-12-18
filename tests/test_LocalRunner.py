from fiddle.MakeBuilder import MakeBuilder
from fiddle.LocalRunner import LocalRunner
from fiddle.Runner import Runnable
from fiddle.Builder import BuildSpec

def test_hello_world():
    
    b = MakeBuilder(BuildSpec("test_src/test.cpp", build_parameters=dict(OPTIMIZE="-O0")))
    build_result = b.build()

    runnable = Runnable(function="simple_print", arguments=dict(a=1, b=2, c=3))
    
    runner = LocalRunner(build_result, runnable)

    invocation_result = runner.run()
    print(invocation_result.results)
