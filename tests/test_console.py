import cfiddle.util
from cfiddle.paths import *

def test_set_ld_path_in_shell():
    success,output = cfiddle.util.invoke_process("set-cfiddle-ld-path")
    assert success
    assert cfiddle_lib_path() in output
    
def test_print_cfiddle_lib_path():
    success, output = cfiddle.util.invoke_process("cfiddle-lib-path")
    assert success
    assert output.strip() == cfiddle_lib_path()

def test_print_cfiddle_include_path():
    success, output = cfiddle.util.invoke_process("cfiddle-include-path")
    assert success
    assert output.strip() == cfiddle_include_path()
