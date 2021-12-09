import pytest
import re
import ctypes
import collections


class BadArgument(Exception):
    pass

class UnknownType(Exception):
    pass
class BadArgumentName(Exception):
    pass

class ProtoParser:

    def can_parse_file(filename):
        raise NotImplementedError("can_parse_file")

    def parse_file(filename):
        raise NotImplementedError("parse_file")

    
Prototype = collections.namedtuple("Prototype", "return_type,name,arguments")
Argument = collections.namedtuple("Argument", "type,name")
