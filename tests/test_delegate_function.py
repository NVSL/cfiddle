from cfiddle import *
import pytest
from fixtures import *
from cfiddle.ext.delegate_function import execution_method

def test_delegate_function(test_cpp):
    try:
        import delegate_function
    except ModuleNotFoundError:
        pytest.skip("delegate_function is not installed.")
    
    with cfiddle_config(RunnerExecutionMethod_type=execution_method("""
version: 0.1
sequence:
  - type: TrivialDelegate
  - type: TrivialDelegate
""")):
        r = run(test_cpp, 'sum', arg_map(a=0,b=1))
        r.as_df()
