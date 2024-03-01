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


def test_exceptions(setup):
    class Handler():
        def handle_exeception(self, e):
            if isinstance(e, CFiddleException):
                echo("Handled")
                return True
            else:
                echo("Not handled")
                return False


    @handle_cfiddle_exceptions
    def mimic_handled_error():
        1/0

    @handle_cfiddle_exceptions
    def mimic_handled_cfiddle_error():
        raise CFiddleException("Handled")

    @handle_cfiddle_exceptions
    def mimic_unhandled_error():
        dict()[1]

    with cfiddle_config():
        enable_debug(enable=False)
        with cfiddle_config(ExceptionHandler_type=Handler):
            mimic_handled_error()
            mimic_handled_cfiddle_error()

            enable_debug(enable=True)
            with pytest.raises(KeyError):
                mimic_unhandled_error()

