import io
import pytest
import re
import os
import ctypes
from .ProtoParser import BadArgument, UnknownType, BadArgumentName, Prototype, Argument, ProtoParser

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

class CProtoParser(ProtoParser):
    def can_parse_file(self, filename):
        _, file_extension = os.path.splitext(filename.strip())
        return file_extension.upper() in [".C", ".CPP", ".H", ".HPP", ".CC"]
    
    def parse_file(self, f):
        try:
            lines = f.readlines()
        except AttributeError:
            with open(f, "r") as t:
                lines = t.readlines()
        finally:
            prototypes = [parse_prototype(l) for l in lines]
            return {x.name: x for x in prototypes if x is not None}
    

type_map = {}
for t, aliases in ctype_decls:
    type_map.update({a:t for a in aliases})

def get_ctype(type_name):
    t = type_name.strip()
    t = re.sub(r"\s+", " ", t)
    t = t.replace(" *", "*")
    if t not in type_map:
        raise UnknownType(type_name)
    return type_map[t]
    

@pytest.mark.parametrize("t,ct", [
    ("void*", ctypes.c_void_p),
    ("void *", ctypes.c_void_p),
    ("long", ctypes.c_long),
    ("uint64_t", ctypes.c_ulonglong)
])
def test_get_ctype(t,ct ):
    assert get_ctype(t) ==ct

def parse_arg(arg):
    arg = re.sub(r"\s+", " ", arg)
    tokens = arg.split()
    if tokens == 1:
        raise BadArgument(arg)
    type_name = " ".join(tokens[:-1])
    name = tokens[-1]
    if not re.match(r"[a-zA-Z0-9_ ]+", type_name):
        raise UnknownType(type_name)
    if not re.match(r"[a-zA-Z0-9_ ]+",name):
        raise BadArgumentName(name)
    type = get_ctype(type_name)

    return Argument(type=type, name=name)

@pytest.mark.parametrize("arg,parsed", [
    ("int bar", Argument(ctypes.c_int, "bar")),
    (" int  bar", Argument(ctypes.c_int, "bar")),
    (" int  bar", Argument(ctypes.c_int, "bar")),
    (" long int  bar", Argument(ctypes.c_long, "bar")),
    (" unsigned long int  bar", Argument(ctypes.c_ulong, "bar"))
])
def test_parse_arg(arg, parsed):
    assert parse_arg(arg) == parsed

def parse_prototype(prototype):

    prototype = re.sub(r"//.*", "", prototype)
    prototype = re.sub(r"/\*.*", "", prototype)
    
    m = re.match(r"\s*((\w+\s*\**\s+)+)(\w+)\s*\((.*)\).*", prototype)
    if m is None:
        return None
    try:
        return_type = m.group(1)
        return_type = get_ctype(return_type)
        function_name = m.group(3)
        parameters = m.group(4)
        if parameters:
            args = parameters.split(",")

            parsed_args = [parse_arg(a) for a in args]
        else:
            parsed_args  = []
    except (BadArgument, UnknownType) as e:
        return None
    return Prototype(return_type=return_type,
                     name=function_name,
                     arguments = parsed_args)


@pytest.mark.parametrize("prototype,parsed", [
    ("void foo()", Prototype(return_type=void,
                             name="foo",
                             arguments=[])),
    ("void foo()//aoeu", Prototype(return_type=void,
                                   name="foo",
                                   arguments=[])),
    ("void foo()/* aoeu", Prototype(return_type=void,
                                   name="foo",
                                   arguments=[])),
    (" void  foo () ", Prototype(return_type=void,
                                 name="foo",
                                 arguments=[])),
    ("void* foo2(uint64_t x, float y);", Prototype(ctypes.c_void_p, "foo2", [Argument(ctypes.c_uint64,"x"),
                                                                             Argument(ctypes.c_float ,"y")])),
    (" void  foo (int bar) ", Prototype(void, "foo", [Argument(ctypes.c_int, "bar")])),
    ("unsigned long int  baz (long int bar) ", Prototype(ctypes.c_ulong, "baz", [Argument(ctypes.c_long, "bar")])),
    ("  ostream out(&filebuf);", None),
    ("object(bar);", None),
    ("void foo3()\n",  Prototype(void, "foo3", []))
])
def test_parse_prototype(prototype, parsed):
    assert parse_prototype(prototype) == parsed
    
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
    

     
@pytest.mark.parametrize("filecontents,protos", [
    ("""
int foo(uint64_t x, float y) {}
void* foo2(uint64_t x, float y);
void foo3()
object(bar);
""", [
    Prototype(ctypes.c_int, "foo", [Argument(ctypes.c_uint64,"x" ),
                                    Argument(ctypes.c_float ,"y" )]),
    Prototype(ctypes.c_void_p, "foo2", [Argument(ctypes.c_uint64,"x"),
                                        Argument(ctypes.c_float ,"y")]),
    Prototype(void, "foo3", [])
]
    ),
    ])
def test_parse_multi_line(filecontents, protos):
    parser = CProtoParser()
    f = io.StringIO(filecontents)
    print(protos)
    assert parser.parse_file(f) == protos
    

     
