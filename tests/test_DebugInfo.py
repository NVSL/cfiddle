from cfiddle import *
from fixtures import *

def print_ident(a):
    print(a)
    return a



def test_DWARF(test_cpp):
    with test_cpp.DWARFInfo() as t:
        assert t is not None;

def test_ELFFile(test_cpp):
    with test_cpp.ELFFile() as t:
        assert t is not None;

def test_complex(setup):
    source = code(r"""
#include<vector>

extern "C" 
int bar(int p) {
    register long int i= 0; 
    register long int a = 4;
    long int j= 0; 
    for(int k = 0; k < 100; k++) {
        return k;
    }
    i = a;
    for(i = 0; i < a; i++) {
        a+=i;
    }
    i = a;
    return j + a; 
}

extern "C" 
int baz(int p) {
    std::vector<int> k;
    int i;
    for(i = 0;i < p; i++) {
        k.push_back(i);
    }
    return k.size();
}""")
    b = build(source, verbose=True, build_parameters=arg_map(DEBUG_FLAGS="-g3"))
    b[0].debug_info()
    
def test_selective(setup):
    source = code(r"""extern "C" int foo(int a) {int k= 0; return k;} extern "C" void bar(){}""")
    b = build(source, verbose=True, build_parameters=arg_map(DEBUG_FLAGS="-g3"))

    assert "DW_AT_low_pc" in print_ident(b[0].debug_info())
    assert "foo" in print_ident(b[0].debug_info())
    assert "bar" in print_ident(b[0].debug_info())
    assert "foo" in print_ident(b[0].debug_info(show="foo"))
    assert "bar" not in print_ident(b[0].debug_info(show="foo"))


def test_stack_frame(test_cpp):
    assert "simple_print" in test_cpp.stack_frame("simple_print") 
