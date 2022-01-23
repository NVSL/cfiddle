from cfiddle import *
from fixtures import setup

def test_hello_world_c(setup):

    run(build(code(r""" 
#include"cfiddle.h"
int DoubleIt(int x) {
    return x * 2;
}
    """, language="c")), "DoubleIt", arg_map(x=[1,2]))


def test_c_source_inspect(setup):

    src=r""" 
void DoubleIt(int x) {
}
"""
    b = build(code(src, language="c"))
    b[0].source()
    assert b[0].source("DoubleIt").strip() == src.strip()


def test_c_measurement(setup):
    r = run(build(code(r""" 
#include"cfiddle.h"
int loop(int x) {
    int sum  = 0;
    start_measurement(NULL);
    for(int i = 0;i < x;i++) {
        sum += i;
    }
    end_measurement();
    return sum;
}
    """, language="c"), verbose=True), "loop", arg_map(x=[10000,100000]))
    print(r.as_df())
