import io
import pytest
import re
import os
import ctypes
from .ProtoParser import BadParameter, UnknownType, BadParameterName, Prototype, Parameter, ProtoParser


class CProtoParser(ProtoParser):
    
    def can_parse_file(self, filename):
        _, file_extension = os.path.splitext(filename.strip())
        return file_extension.upper() in [".C", ".CPP", ".H", ".HPP", ".CC"]

    
    def parse_file(self, f):
        lines = self.detect_file_type_and_read_lines(f)
        prototypes = [parse_prototype(l) for l in lines]
        return {x.name: x for x in prototypes if x is not None}

    
    def detect_file_type_and_read_lines(self, f):
        try:
            return f.readlines()
        except AttributeError:
            with open(f, "r") as t:
                return t.readlines()


def parse_prototype(prototype):

    prototype = strip_comments(prototype)
    prototype = strip_extern_c(prototype)
    
    r = split_prototype(prototype)
    if r is None:
        return None
    
    return_type_string, function_name, parameters = r
        
    try:
        parsed_parameters = parse_parameters(parameters)
        return_type =parse_return_type(return_type_string)
    except (BadParameter, UnknownType) as e:
        return None

    return Prototype(return_type=return_type,
                     name=function_name,
                     parameters = parsed_parameters)


def parse_return_type(return_type_string):
    tokens = split_into_tokens(return_type_string)
    tokens = remove_keywords(tokens)
    
    raise_on_invalid_type(tokens)
    
    return get_ctype(tokens)


def parse_parameter(parameter):

    tokens = split_into_tokens(parameter)

    if len(tokens) <= 1:
        raise BadParameter(parameter)

    tokens = remove_keywords(tokens)

    type_name = " ".join(tokens[:-1])
        
    name = tokens[-1]

    raise_on_invalid_type(tokens)
    raise_on_invalid_name(name)

    return Parameter(type=get_ctype(tokens[:-1]), name=name)


def raise_on_invalid_type(tokens):
    if len(tokens) == 0:
        raise UnknownType("Empty type")
    if not all([re.match(r"[a-zA-Z0-9_]+", t) for t in tokens[:-1]]):
        raise UnknownType(" ".join(tokens))
    if not re.match(r"[a-zA-Z0-9_]+[\*\&]*", tokens[-1]):
        raise UnknownType(" ".join(tokens))

    
def raise_on_invalid_name(name):
    if not re.match(r"[a-zA-Z0-9_]+",name):
        raise BadParameterName(name)


def split_into_tokens(parameter):

    # collect * and & on last component of type
    parameter = re.sub(r"\s*\*", "*", parameter)
    parameter = re.sub(r"\s*&", "&", parameter)
    parameter = re.sub(r"[*&]+", "\g<0> ", parameter)
    return re.sub(r"\s+", " ", parameter).split()

@pytest.mark.parametrize("string,tokens", [
    ("unsigned int* foo", ["unsigned", "int*", "foo"]),
    ("unsigned int& foo", ["unsigned", "int&", "foo"]),
    ("unsigned int** foo", ["unsigned", "int**", "foo"]),
    ("unsigned int * &  foo", ["unsigned", "int*&", "foo"]),
    ("unsigned int foo", ["unsigned", "int", "foo"]),
    ("unint64_t *array", ["unint64_t*", "array"])
])
def test_split_into_tokens(string, tokens):
    assert split_into_tokens(string) == tokens
    
def remove_keywords(split_parameter):
    return list(filter(lambda x: x not in ["register", "const", "volatile", "inline", "return"], split_parameter))
    

def strip_comments(line):
    line = re.sub(r"//.*",  "", line)
    line = re.sub(r"/\*.*", "", line)
    return line

def strip_extern_c(line):
    return re.sub(r"extern\s*\"C\"\s*", "", line)


def split_prototype(prototype):
    #                   typeparts  lastpart    starsorspace   maybe    an     attribute          name    parameters
    m =  re.match(r"\s*(((\w+\s+)*(\w+\s*))\s*(\s+|(\*+\s*)))(\s*__attribute__\s*\(\(.*\)\)\s*)?(\w+)\s*\((.*)\).*", prototype)
    if m is None:
        return None

    return  m.group(1), m.group(8), m.group(9)


def parse_parameters(parameter_string):
    if parameter_string:
        return [parse_parameter(a) for a in parameter_string.split(",")]
    else:
        return []

class UnhandledIndirectParameterType:
    def __init__(self, name):
        self.name = name
        
    def __call__(self, *argc, **kwargs):
        raise UnknownType(f"Can't pass arguments of type '{name}'")

def get_ctype(type_tokens):
    type_name = " ".join([t.strip() for t in type_tokens])
    
    if "*" in type_name or "&" in type_name:
        return UnhandledIndirectParameterType(type_name)

    if type_name not in type_map:
        raise UnknownType(type_name)
    
    return type_map[type_name]

def extract_stars_and_amps(token):
    m = re.match(r"([a-zA-Z0-9_]+)([\*\&]*)", token)
    return m.group(1),  m.group(2)
    
void="void"

ctype_decls = [
    (ctypes.c_bool , ["_Bool"]),
    (ctypes.c_wchar , ["wchar_t"]),
    (ctypes.c_byte , ["char"]),
    (ctypes.c_int8, ["int8_t"]),
    (ctypes.c_int16, ["int16_t"]),
    (ctypes.c_int32, ["int32_t"]),
    (ctypes.c_int64, ["int64_t"]),
    (ctypes.c_uint8, ["uint8_t"]),
    (ctypes.c_uint16, ["uint16_t"]),
    (ctypes.c_uint32, ["uint32_t"]),
    (ctypes.c_uint64, ["uint64_t"]),
    (ctypes.c_ubyte , ["unsigned char"]),
    (ctypes.c_short , ["short"]),
    (ctypes.c_ushort , ["unsigned short"]),
    (ctypes.c_int , ["int"]),
    (ctypes.c_uint , ["unsigned int"]),
    (ctypes.c_long , ["long", "long int"]),
    (ctypes.c_ulong , ["unsigned long", "unsigned long int"]),
    (ctypes.c_longlong , ["long long"]),
    (ctypes.c_ulonglong , ["unsigned long long"]),
    (ctypes.c_size_t , ["size_t"]),
    (ctypes.c_ssize_t , ["ssize_t"]),
    (ctypes.c_float , ["float"]),
    (ctypes.c_double , ["double"]),
    (ctypes.c_longdouble , ["long double"]),
    (ctypes.c_char_p , ["char*"]),
    (ctypes.c_wchar_p , ["wchar_t*"]),
    (ctypes.c_void_p , ["void*"]),
    (void, ["void"])
]


type_map = {}
for t, aliases in ctype_decls:
    type_map.update({a:t for a in aliases})

@pytest.mark.parametrize("t,ct", [
    ("long", ctypes.c_long),
    ("uint64_t", ctypes.c_ulonglong)
])
def test_get_ctype(t,ct ):
    assert get_ctype(t.split()) ==ct

@pytest.mark.parametrize("t,ct", [
    ("void*", UnhandledIndirectParameterType),
    ("void *", UnhandledIndirectParameterType),
    ("long int *", UnhandledIndirectParameterType)
])
def test_unhandled_get_ctype(t,ct ):
    assert isinstance(get_ctype(t), ct)


@pytest.mark.parametrize("parameter,parsed", [
    ("int bar", Parameter(ctypes.c_int, "bar")),
    (" int  bar", Parameter(ctypes.c_int, "bar")),
    (" int  bar", Parameter(ctypes.c_int, "bar")),
    (" long int  bar", Parameter(ctypes.c_long, "bar")),
    (" unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
    ("register unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
    ("register const unsigned long int  bar", Parameter(ctypes.c_ulong, "bar")),
])
def test_parse_parameter(parameter, parsed):
    assert parse_parameter(parameter) == parsed


@pytest.mark.parametrize("prototype,parsed", [
    ("void foo()", Prototype(return_type=void,
                             name="foo",
                             parameters=[])),
    ("void foo()//aoeu", Prototype(return_type=void,
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
def test_parse_prototype(prototype, parsed):
    assert parse_prototype(prototype) == parsed

@pytest.mark.parametrize("prototype,parsed", [
    ("void* foo2(uint64_t x, float y);", Prototype(None, "foo2", [Parameter(ctypes.c_uint64,"x"),
                                                                  Parameter(ctypes.c_float ,"y")]))])
def test_parse_prototype_unhandled_types(prototype, parsed):
    assert isinstance(parse_prototype(prototype).return_type, UnhandledIndirectParameterType)

    
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
def test_can_parse(filename, good):
    parser = CProtoParser()
    assert parser.can_parse_file(filename) == good

@pytest.mark.parametrize("line", [
    ("        return getpid();")
])
def test_things_that_are_not_functions(line):
    assert parse_prototype(line) == None

     
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
def test_parse_multi_line(filecontents, protos):
    parser = CProtoParser()
    f = io.StringIO(filecontents)
    assert parser.parse_file(f) == protos
    
@pytest.mark.parametrize("prototype", [
    (r"""uint64_t** loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t *loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t * loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""uint64_t*loop_func(uint64_t  *array, unsigned long int size) {"""),
    (r"""void* foo2(uint64_t x, float y);""")
])
def test_parse_unhandled_parameter(prototype):
    parser = CProtoParser()
    f = io.StringIO(prototype)
    prototypes = parser.parse_file(f)
    assert len(prototypes) == 1

     
