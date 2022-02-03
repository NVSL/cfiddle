import pytest
import re
import ctypes
import collections

from .Exceptions import CFiddleException


class BadParameter(CFiddleException):
    pass

class UnknownType(CFiddleException):
    pass

class BadParameterName(CFiddleException):
    pass

class ProtoParser:

    def can_parse_file(filename):
        raise NotImplementedError("can_parse_file")

    def parse_file(filename):
        raise NotImplementedError("parse_file")

    
Prototype = collections.namedtuple("Prototype", "return_type,name,parameters")
Parameter = collections.namedtuple("Parameter", "type,name")
