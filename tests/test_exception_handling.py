import pytest
from cfiddle import *
from cfiddle.config import cfiddle_config, enable_debug, in_debug, get_config
from click import echo

def test_debug():

    with pytest.raises(CFiddleException):
        b = build(code(""), arg_map(a=[[1,1],1]))
        
    with cfiddle_config():
        enable_debug()
        try:
            b = build(code(""), arg_map(a=[[1,1],1]))
        except Exception as e:
            t = e
        assert t.__context__ == None
    assert not in_debug()

    with cfiddle_config():
        enable_interactive()
        b = build(code(""), arg_map(a=[[1,1],1])) # shouldn't raise



    
