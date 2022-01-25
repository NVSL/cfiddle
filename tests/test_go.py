import os
import pytest

from cfiddle import *
import cfiddle
from fixtures import setup
from util import skip_if_go_not_available

def test_hello_world_build(setup):
    skip_if_go_not_available()

    src = code(r""" 

//export DoubleIt
func DoubleIt(x int) int {
        return x * 2
}
    """, language="go")

    r = build(src)

    assert os.path.exists(r[0].lib)

    
def test_hello_world_go(setup):
    skip_if_go_not_available()

    run(build(code(r""" 

//export DoubleIt
func DoubleIt(x int) int {
        return x * 2
}
    """, language="go")), "DoubleIt", arg_map(x=[1,2]))


def test_decoration(setup):
    raw = r"""
func loop() {}
"""
    source = code(raw, language="go")
    decorated_source = cfiddle.util.read_file(source)
    decorated_lines = decorated_source.split("\n")
    assert "package main" in decorated_lines[1]
    assert raw in decorated_source

    undecorated_source = cfiddle.util.read_file(code(raw, language="go", raw=True))
    undecorated_lines = undecorated_source.split("\n")
    assert "package main" not in undecorated_lines[1]
    assert raw in undecorated_source
                  

def test_go_inspection(setup):
    skip_if_go_not_available()

    b = build(code(r""" 
//export loop
func loop(x int) int {
    sum := 0
    C.start_measurement(nil)
    for i := 0; i < x; i++ {
        sum += i;
    }
    C.start_measurement(nil)
    return sum
}

    """, language="go"), verbose=True)

    print(b[0].source())

    
def test_go_function_extraction(setup):
    skip_if_go_not_available()
    src = r""" 
//export loop
func loop(x int){
}
"""
    b = build(code(src, language="go"), verbose=True)

    assert b[0].source("loop").strip() ==  """func loop(x int){
}"""

    
def test_go_measurement(setup):
    skip_if_go_not_available()

    run(build(code(r""" 
//export loop
func loop(x int) int {
    sum := 0
    C.start_measurement(nil)
    for i := 0; i < x; i++ {
        sum += i;
    }
    C.start_measurement(nil)
    return sum
}

    """, language="go"), verbose=True), "loop", arg_map(x=[10000,100000]))

def test_compile_options(setup):
    pytest.skip("Not sure how to set this effectively")
    skip_if_go_not_available()

    build(code(r""" 
    //export loop
func loop(x int) {
    }
    """, language="go"), verbose=True, build_parameters=arg_map(OPTMIZE=["","-N"]))
    
def test_assembly(setup):
    pytest.skip("Not sure how to generate assembly")
    skip_if_go_not_available()

    b = build(code(r""" 
    //export loop
func loop(x int) {
    }
    """, language="go"), verbose=True)
    
    b[0].asm()
