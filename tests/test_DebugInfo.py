from cfiddle import *
from fixtures import *

def print_ident(a):
    print(a)
    return a

def test_debug_info(setup):
    source = code(r"""extern "C" int foo(int a) {int k= 0; return k;} extern "C" void bar(){}""")
    b = build(source, verbose=True, build_parameters=arg_map(DEBUG_FLAGS="-g3"))

    assert "DW_AT_low_pc" in print_ident(b[0].debug_info())
    assert "foo" in print_ident(b[0].debug_info())
    assert "bar" in print_ident(b[0].debug_info())
    assert "foo" in print_ident(b[0].debug_info(show="foo"))
    assert "bar" not in print_ident(b[0].debug_info(show="foo"))


def test_DWARF(test_cpp):
    with test_cpp.DWARFInfo() as t:
        assert t is not None;
    source = code(r"""extern "C" int foo(int a) {int k= 0; return k;} extern "C" void bar(){}""")
    b = build(source, verbose=True, build_parameters=arg_map(DEBUG_FLAGS=""))
    with b[0].DWARFInfo() as t:
        assert t is None

def test_ELFFile(test_cpp):
    with test_cpp.ELFFile() as t:
        assert t is not None;
