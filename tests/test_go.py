from cfiddle import *
from util import skip_if_go_not_available
import os

def test_hello_world_build():
    skip_if_go_not_available()

    src = code(r""" 
package main

import "C"

//export DoubleIt
func DoubleIt(x int) int {
        return x * 2
}

func main() {}

    """, language="go")

    r = build(src)

    assert os.path.exists(r[0].lib)

    
def test_hello_world_go():
    skip_if_go_not_available()

    run(build(code(r""" 
package main

import "C"

//export DoubleIt
func DoubleIt(x int) int {
        return x * 2
}

func main() {}

    """, language="go")), "DoubleIt", arg_map(x=[1,2]))


def test_go_measurement():
    skip_if_go_not_available()

    run(build(code(r""" 
package main

// #cgo LDFLAGS: -L/cse142L/fiddle/src/cfiddle/resources/libcfiddle/build  -lcfiddle
// #cgo CFLAGS: -g -Wall -I/cse142L/fiddle/src/cfiddle/resources/include
// #include "cfiddle.h"
import "C"

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

    """, language="go")), "loop", arg_map(x=[10000,100000]))

