import io
import pytest
import re
import os
import ctypes
from .ProtoParser import BadParameter, UnknownType, BadParameterName, Prototype, Parameter, ProtoParser

class CLikeProtoParser(ProtoParser):

    def can_parse_file(self, filename):
        _, file_extension = os.path.splitext(filename.strip())
        return file_extension.upper() in self.known_file_extensions

    
    def parse_file(self, f):
        lines = self._detect_file_object_type_and_read_lines(f)
        prototypes = [self.parse_prototype(l) for l in lines]
        return {x.name: x for x in prototypes if x is not None}

    
    def __init__(self):

        self.type_map = {}
        for t, aliases in self.ctype_decls:
            self.type_map.update({a:t for a in aliases})

    
    def _detect_file_object_type_and_read_lines(self, f):
        try:
            return f.readlines()
        except AttributeError:
            with open(f, "r") as t:
                return t.readlines()

    def parse_prototype(self, prototype):

        prototype = self.strip_comments_and_decorations(prototype)

        r = self.split_prototype(prototype)
        if r is None:
            return None

        return_type_string, function_name, parameters = r

        try:
            parsed_parameters = self.parse_parameters(parameters)
            return_type = self.parse_return_type(return_type_string)
        except (BadParameter, UnknownType) as e:
            return None

        return Prototype(return_type=return_type,
                         name=function_name,
                         parameters = parsed_parameters)


    def parse_return_type(self, return_type_string):
        if return_type_string:
            tokens = self.split_into_tokens(return_type_string)
            tokens = self.remove_keywords(tokens)
            
            self.raise_on_invalid_type(tokens)
            
            return self.get_ctype(tokens)
        else:
            return None

        
    def extract_type_and_name_tokens(self, tokens):
        """
        Return a list of tokens that the describe the type and a string that gives the name of the parameter
        """
        raise NotImplementedError("extract_type_and_name_tokens")


    def parse_parameter(self, parameter):
        
        tokens = self.split_into_tokens(parameter)
        tokens = self.remove_keywords(tokens)

        if len(tokens) <= 1:
            raise BadParameter(parameter)

        type_tokens, name = self.extract_type_and_name_tokens(tokens)

        self.raise_on_invalid_type(tokens)
        self.raise_on_invalid_name(name)

        return Parameter(type=self.get_ctype(type_tokens), name=name)


    def raise_on_invalid_type(self, tokens):
        if len(tokens) == 0:
            raise UnknownType("Empty type")
        if not all([re.match(r"[a-zA-Z0-9_]+", t) for t in tokens[:-1]]):
            raise UnknownType(" ".join(tokens))
        if not re.match(r"[a-zA-Z0-9_]+[\*\&]*", tokens[-1]):
            raise UnknownType(" ".join(tokens))


    def raise_on_invalid_name(self, name):
        if not re.match(r"[a-zA-Z0-9_]+",name):
            raise BadParameterName(name)


    def split_into_tokens(self, parameter):
        # collect * and & on last component of type
        parameter = re.sub(r"\s*\*", "*", parameter)
        parameter = re.sub(r"\s*&", "&", parameter)
        parameter = re.sub(r"[*&]+", "\g<0> ", parameter)
        return re.sub(r"\s+", " ", parameter).split()


    def remove_keywords(self, split_parameter):
        return list(filter(lambda x: x not in self.type_modifiers_to_remove, split_parameter))

    
    def strip_comments_and_decorations(self, line):
        for regex in self.regexes_to_strip_out:
            line = re.sub(regex,  "", line)
        return line


    def parse_parameters(self, parameter_string):
        if parameter_string:
            return [self.parse_parameter(a) for a in parameter_string.split(",")]
        else:
            return []

    def get_ctype(self, type_tokens):
        type_name = " ".join([t.strip() for t in type_tokens])

        if "*" in type_name or "&" in type_name:
            return UnhandledIndirectParameterType(type_name)

        if type_name not in self.type_map:
            raise UnknownType(type_name)

        return self.type_map[type_name]

    def extract_stars_and_amps(self, token):
        m = re.match(r"([a-zA-Z0-9_]+)([\*\&]*)", token)
        return m.group(1),  m.group(2)


class funcptr_t(object):
    def __init__(self, function_name):
        self.function_name = function_name
        self.value = function_name
    
class CProtoParser(CLikeProtoParser):

    def __init__(self):
        self.ctype_decls = [
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
            (ctypes.c_uint , ["unsigned int", 'uint']),
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
            (funcptr_t, ["funcptr_t"]),
            (void, ["void"])
        ]

        super().__init__()

        self.known_file_extensions = [".C", ".CPP", ".H", ".HPP", ".CC", ".CXX", ".C++"]
        self.regexes_to_strip_out = [r"//.*", r"/\*.*", r"extern\s*\"C\"\s*"]
        self.type_modifiers_to_remove = ["register", "const", "volatile", "inline", "return"]
        
    def split_prototype(self, prototype):
        #                   typeparts  lastpart    starsorspace   maybe    an     attribute          name    parameters
        m =  re.match(r"\s*(((\w+\s+)*(\w+\s*))\s*(\s+|(\*+\s*)))(\s*__attribute__\s*\(\(.*\)\)\s*)?(\w+)\s*\((.*)\).*", prototype)
        if m is None:
            return None

        return_type, function_name, parameters = (m.group(1), m.group(8), m.group(9))
        return  return_type, function_name, parameters

    def extract_type_and_name_tokens(self, tokens):
        return tokens[:-1], tokens[-1]


class UnhandledIndirectParameterType:
    def __init__(self, name):
        self.name = name
        
    def __call__(self, *argc, **kwargs):
        raise UnknownType(f"Can't pass arguments of type '{self.name}'")

    
void="void"
