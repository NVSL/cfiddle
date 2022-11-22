import pytest
from cfiddle import *
from cfiddle.Exceptions import handle_cfiddle_exceptions
from cfiddle.config import cfiddle_config, enable_debug, in_debug, get_config
from click import echo
from fixtures import *

def test_debug(setup):

    @handle_cfiddle_exceptions
    def mimic_internal_error():
        1/0
        
    with pytest.raises(CFiddleException):
        b = build(code(""), arg_map(a=[[1,1],1]))

    with cfiddle_config():
        enable_debug(enable=False)
        with cfiddle_config():
            enable_debug()
            try:
                mimic_internal_error()
            except Exception as e:
                t = e
            assert t.__context__ == None
        assert not in_debug()

    with cfiddle_config():
        enable_debug(enable=False)
        try:
            mimic_internal_error()
        except Exception as e:
            t = e
            assert t.__context__ != None # this means we didn't wrap the exception in our own.



    
