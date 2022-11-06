import io
import pytest
import re
import os
import ctypes
from cfiddle.CProtoParser import *
from cfiddle.ProtoParser import BadParameter, UnknownType, BadParameterName, Prototype, Parameter

@pytest.mark.parametrize("t,ct", [
    ("long", ctypes.c_long),
    ("uint64_t", ctypes.c_ulonglong)
])
def test_get_ctype(CParser, t,ct):
    assert CParser.get_ctype(t.split()) ==ct

@pytest.mark.parametrize("t,ct", [
    ("void*", UnhandledIndirectParameterType),
    ("void *", UnhandledIndirectParameterType),
    ("long int *", UnhandledIndirectParameterType)
])
def test_unhandled_get_ctype(CParser,t,ct):
    parsed_type = CParser.get_ctype(t)
    assert isinstance(parsed_type, ct)
    with pytest.raises(UnknownType):
        parsed_type()

@pytest.mark.parametrize("parameter,parsed", [
    ("int bar", Parameter(ctypes.c_int, "bar")),
    (" int  bar", Parameter(ctypes.c_int, "bar")),
    (" int  bar", Parameter(ctypes.c_int, "bar")),
    (" uint  bar", Parameter(ctypes.c_uint, "bar")),
    (" long int  bar", Parameter(ctypes.c_long, "bar")),
    (" unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
    ("register unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
    ("register const unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
])
def test_parse_parameter(CParser,parameter, parsed):
    assert CParser.parse_parameter(parameter) == parsed


@pytest.mark.parametrize("prototype,parsed", [
    ("void foo()", Prototype(return_type=void,
                             name="foo",
                             parameters=[])),
    ("void foo()//aoeu", Prototype(return_type=void,
                                   name="foo",
                                   parameters=[])),
    ("int foo() {return 4;}", Prototype(return_type=ctypes.c_int,
                                        name="foo",
                                        parameters=[])),
    ("void foo()/* aoeu", Prototype(return_type=void,
                                   name="foo",
                                   parameters=[])),
    (" void  foo () ", Prototype(return_type=void,
                                 name="foo",
                                 parameters=[])),
    (" void  foo (int bar) ", Prototype(void, "foo", [Parameter(ctypes.c_int, "bar")])),
    ("unsigned long int  baz (long int bar) ", Prototype(ctypes.c_ulong, "baz", [Parameter(ctypes.c_long, "bar")])),
    ("  ostream out(&filebuf);", None),
    ("object(bar);", None),
    ("void foo3()\n",  Prototype(void, "foo3", [])),
    ("inline int foo3()\n",  Prototype(ctypes.c_int, "foo3", [])),
    ("int inline __attribute__ ((used)) foo()", Prototype(ctypes.c_int, "foo", [])),
    ("int __attribute__((used)) foo()", Prototype(ctypes.c_int, "foo", [])),
    ('int __attribute__((optimize("noinline")) foo(int bar)', Prototype(ctypes.c_int, "foo", [Parameter(ctypes.c_int, "bar")]))
])
def test_parse_prototype(CParser,prototype, parsed):
    assert CParser.parse_prototype(prototype) == parsed

    
@pytest.mark.parametrize("prototype,parsed", [
    ("void* foo2(uint64_t x, float y);", Prototype(None, "foo2", [Parameter(ctypes.c_uint64,"x"),
                                                                  Parameter(ctypes.c_float ,"y")]))])
def test_parse_prototype_unhandled_types(CParser,prototype, parsed):
    assert isinstance(CParser.parse_prototype(prototype).return_type, UnhandledIndirectParameterType)

    
@pytest.mark.parametrize("filename,good", [
    ("foo.cpp", True),
    ("foo.hpp", True),
    ("baz/foo.hpp", True),
    ("baz/foo.hpp ", True),
    ("baz/foo.cc", True),
    ("baz/foo.c", True),
    ("baz/foo.h", True),
    ("baz/foo.d", False),
    ("baz/foo.rs", False)
    ])
def test_can_parse(CParser,filename, good):
    assert CParser.can_parse_file(filename) == good

@pytest.mark.parametrize("line", [
    ("        return getpid();")
])
def test_things_that_are_not_functions(CParser,line):
    assert CParser.parse_prototype(line) == None

     
@pytest.mark.parametrize("filecontents,protos", [
    ("""
int foo(uint64_t x, float y) {}
int foo2(uint64_t x, float y);
void foo3()
object(bar);
""", dict(foo=Prototype(ctypes.c_int, "foo", [Parameter(ctypes.c_uint64,"x" ),
                                    Parameter(ctypes.c_float ,"y" )]),
          foo2=Prototype(ctypes.c_int, "foo2", [Parameter(ctypes.c_uint64,"x"),
                                        Parameter(ctypes.c_float ,"y")]),
          foo3=Prototype(void, "foo3", []))
    )
    ])
def test_parse_multi_line(CParser,filecontents, protos):
    f = io.StringIO(filecontents)
    assert CParser.parse_file(f) == protos
    
@pytest.mark.parametrize("prototype", [
    (r"""uint64_t** loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t *loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t * loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t*loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""void* foo2(uint64_t x, float y);""")
])
def test_parse_unhandled_parameter(CParser,prototype):
    f = io.StringIO(prototype)
    prototypes = CParser.parse_file(f)
    assert len(prototypes) == 1

     

@pytest.mark.parametrize("string,tokens", [
    ("unsigned int* foo", ["unsigned", "int*", "foo"]),
    ("unsigned int& foo", ["unsigned", "int&", "foo"]),
    ("unsigned int** foo", ["unsigned", "int**", "foo"]),
    ("unsigned int * &  foo", ["unsigned", "int*&", "foo"]),
    ("unsigned int foo", ["unsigned", "int", "foo"]),
    ("unint64_t *array", ["unint64_t*", "array"])
])
def test_split_into_tokens(CParser,string, tokens):
    assert CParser.split_into_tokens(string) == tokens
    
@pytest.fixture
def CParser():
    return CProtoParser()
