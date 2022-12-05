import hashlib
import collections
from .CProtoParser import CProtoParser
from .util import arg_map, read_file, ListDelegator, type_check, type_check_list, infer_language
from .Exceptions import *
import types
import os
import pytest


class ExecutableDescription:
    def __init__(self, source=None, build_parameters=None):
        self.source_file = source
        self.build_parameters = build_parameters
        self._raise_on_invalid_types()

    def _raise_on_invalid_types(self):
        try:
            type_check(self.source_file, str)
        except (TypeError, ValueError) as e:
            raise CFiddleException(e)
            
        try:
            type_check_list(self.build_parameters.keys(), str)
        except (ValueError, TypeError) as e:
            raise InvalidBuildParameter(e)

        for v in self.build_parameters.values():
            if not any([isinstance(v, t) for t in [int, str, float]]) or isinstance(v, bool): # bool is an int!
                raise InvalidBuildParameter(f"Can't have '{v}' as build_parameter value.")
        
    def get_language(self):
        return infer_language(self.source_file)

    def get_build_parameters(self):
        return self.build_parameters

    def set_build_parameter(self, name, value):
        self.build_parameters[name] = value

        
class Executable:

    def __init__(self, lib, toolchain, build_dir, output, build_command, build_spec, functions):
        self.lib = lib
        self.build_dir = build_dir
        self.output = output
        self.build_command = build_command
        self.build_spec = build_spec
        self.functions = functions
        self.toolchain = toolchain
        self._raise_on_invalid_types()
    

    def get_toolchain(self):
        return self.toolchain
        
    def compute_built_filename(self, filename):
        return os.path.join(self.build_dir, filename)
    
    def extract_build_name(self, filename):
        _, source_name = os.path.split(self.build_spec.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

    def get_build_parameters(self):
        """
        Returns a map containing the build parameters that :func:`cfiddle.build()` used when building it via :code:`get_build_parameters()`.
        """
        
        return self.build_spec.build_parameters

    def get_toolchain(self):
        return self.toolchain
    
    def _raise_on_invalid_types(self):
        type_check(self.lib, str)
        type_check(self.build_dir, str)
        type_check(self.build_command, str)
        type_check(self.build_spec, ExecutableDescription)
        type_check(self.functions, dict)
        type_check_list(self.functions.keys(), str)
        

class Builder:
    
    def __init__(self, build_spec, build_root=None, parsers=None, result_factory=None):
        from .config import get_config
        
        self.build_spec = build_spec
        self.source_file = build_spec.source_file
        self.result_factory = result_factory or get_config("Executable_type")
        self.parsers = parsers or get_config("ProtoParser_types")
        self.source_name_base = self._compute_source_name_base()
        self.build_parameters = build_spec.build_parameters

        self.build_root = build_root

        if self.build_root is None:
            self.build_root = os.path.join(os.environ.get("CFIDDLE_BUILD_ROOT", get_config("CFIDDLE_BUILD_ROOT")), "build")

        self.build_directory = self._compute_build_directory()

        self._select_parser()

    
    def build(self):
        raise NotImplemented

    def _compute_build_directory(self):
        m = hashlib.md5()
        build_options = "__".join([f"{p}_{str(v).replace(' ', '').replace('=','_').replace('/','_')}" for p,v in self.build_parameters.items()])
        m.update(build_options.encode())
        return os.path.join(self.build_root, f"{m.hexdigest()}_{self.source_name_base}")
    
    def _compute_source_name_base(self):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

    def _select_parser(self):
        for parser_type in self.parsers:
            p = parser_type()
            if p.can_parse_file(self.source_file):
                self.parser = p
                return
        raise UnknownFileType(f"No parser is available for file '{self.source_file}'.")


class ExecutableList(list):
    """Collect results of compilation.
    
    A collection of compiled code (e.g., returned by
    :func:`build()`).

    The columns of the table include:

    1.  Build parameters.
    2.  Source file.

    You can also call :method:`rebuild()` to recompile with the latest
    version of the undedrlying source code.
    """

    def __add__(self, rhs):
        #https://stackoverflow.com/a/8180577/3949036
        return ExecutableList(list.__add__(self,rhs))

    def __radd__(self, lhs):
        if not isinstance(lhs, list):
            raise TypeError("Can only add to lists")
        
        return ExecutableList(list.__add__(lhs, self))

    def __getitem__(self, item):
        #https://stackoverflow.com/a/8180577/3949036
        result = list.__getitem__(self, item)
        try:
            return ExecutableList(result)
        except TypeError:
            return result

    def rebuild(self):
        from cfiddle import build_list
        build_specs = [dict(source=b.build_spec.source_file, build_parameters=b.build_spec.build_parameters) for b in self]
        return build_list(build_specs)
        
    
class BuildFailure(CFiddleException):
    def __str__(self):
        return f"Build command failed:\n\n{self.args[0]}\n\n{self.args[1]}"
    
class InvalidBuildParameter(CFiddleException):
    pass

class UnknownFileType(CFiddleException):
    pass

