import collections
from .CProtoParser import CProtoParser
from .util import arg_map, read_file, ListDelegator, type_check, type_check_list
import types
import os
import pytest

class ExecutableDescription:
    def __init__(self, source=None, build_parameters=None):
        self.source_file = source
        self.build_parameters = build_parameters

        self._raise_on_invalid_types()

    def _raise_on_invalid_types(self):
        type_check(self.source_file, str)
        type_check_list(self.build_parameters.keys(), str)
        for v in self.build_parameters.values():
            if not any([isinstance(v, t) for t in [int, str, float]]) or isinstance(v, bool): # bool is an int!
                raise ValueError(f"Can't have '{v}' as build_parameter value.")


class Executable:

    def __init__(self, lib, build_dir, output, build_command, build_spec, functions):
        self.lib = lib
        self.build_dir = build_dir
        self.output = output
        self.build_command = build_command
        self.build_spec = build_spec
        self.functions = functions

        self._raise_on_invalid_types()
    
    
    def compute_built_filename(self, filename):
        return os.path.join(self.build_dir, filename)

    
    def extract_build_name(self, filename):
        _, source_name = os.path.split(self.build_spec.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base


    def get_default_function_name(self):
        if len(self.functions) == 1:
            return list(self.functions.values())[0].name
        else:
            raise ValueError(f"There's is not exactly one function ({list(self.functions.keys())}), so you need to provide one.")

    def get_build_parameters(self):
        return self.build_spec.build_parameters
        
    def _raise_on_invalid_types(self):
        type_check(self.lib, str)
        type_check(self.build_dir, str)
        type_check(self.build_command, str)
        type_check(self.build_spec, ExecutableDescription)
        type_check(self.functions, dict)
        type_check_list(self.functions.keys(), str)
        

class Builder:
    
    def __init__(self, build_spec, build_root=None, parser=None, result_factory=None):
        from .config import get_config
        
        self.build_spec = build_spec
        self.source_file = build_spec.source_file
        self.result_factory = result_factory or get_config("Executable_type")
        self.parser = parser or get_config("ProtoParse_type")()
        self.source_name_base = self._compute_source_name_base()
        self.build_parameters = build_spec.build_parameters

        self.build_root = build_root

        if self.build_root is None:
            self.build_root = os.path.join(os.environ.get("CFIDDLE_BUILD_ROOT", get_config("CFIDDLE_BUILD_ROOT")), "build")

        self.build_directory = self._compute_build_directory()

        
    def build(self):
        raise NotImplemented

    
    def _compute_build_directory(self):
        return os.path.join(self.build_root, "__".join([f"{p}_{v.replace(' ', '')}" for p,v in self.build_parameters.items()]) + "_" + self.source_name_base)

    
    def _compute_source_name_base(self):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base


class BuildFailure(Exception):
    def __str__(self):
        return f"Build command failed:\n\n{self.args[0]}\n\n{self.args[1]}"
    
class BadBuildParameter(Exception):
    pass
