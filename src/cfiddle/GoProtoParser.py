import pytest
import re
import ctypes
from .ProtoParser import BadParameter, UnknownType, BadParameterName, Prototype, Parameter
from .CProtoParser import CLikeProtoParser


class GoProtoParser(CLikeProtoParser):
    def __init__(self):

        self.ctype_decls = [
            (ctypes.c_bool , ["bool"]),
            (ctypes.c_byte , ["byte", "uint8"]),
            (ctypes.c_int8, ["int8"]),
            (ctypes.c_int16, ["int16"]),
            (ctypes.c_int32, ["int32", "rune"]),
            (ctypes.c_int64, ["int64"]),
            (ctypes.c_uint8, ["uint8"]),
            (ctypes.c_uint16, ["uint16"]),
            (ctypes.c_uint32, ["uint32"]),
            (ctypes.c_uint64, ["uint64"]),
            (ctypes.c_int , ["int"]),
            (ctypes.c_uint , ["uint", "uintptr"])
        ]

        super().__init__()

        self.known_file_extensions = [".GO"]
        self.type_modifiers_to_remove = []
        self.regexes_to_strip_out = [r"//.*"]
                
    def split_prototype(self, prototype):
        #                   typeparts  lastpart    starsorspace   maybe    an     attribute          name    parameters
        #m =  re.match(r"\s*(((\w+\s+)*(\w+\s*))\s*(\s+|(\*+\s*)))(\s*__attribute__\s*\(\(.*\)\)\s*)?(\w+)\s*\((.*)\).*", prototype)

        #                        funcname   param     rtype

        m = re.match(r"\s*func\s+(\w+)\s*\((.*)\)\s*(\w+)?.*", prototype)
        if m is None:
            return None

        return_type, function_name, parameters = (m.group(3), m.group(1), m.group(2))
        return  return_type, function_name, parameters

    def extract_type_and_name_tokens(self, tokens):
        assert len(tokens) == 2, "Go type parsing needs work"
        return [tokens[1]], tokens[0]

