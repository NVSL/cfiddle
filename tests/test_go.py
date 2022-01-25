from cfiddle import *
import cfiddle
from fixtures import setup
from util import skip_if_go_not_available
import os

def test_hello_world_build(setup):
    skip_if_go_not_available()

    src = code(r""" 

//export DoubleIt
func DoubleIt(x int) int {
        return x * 2
}

func main() {}

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

func main() {}

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

func main() {}

    """, language="go"), verbose=True), "loop", arg_map(x=[10000,100000]))

