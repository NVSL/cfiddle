import collections
from .CProtoParser import CProtoParser
from .util import expand_args, read_file, ListDelegator
import types
import os
import pytest

ExecutableDescription = collections.namedtuple("ExecutableDescription", "source_file,build_parameters")

_Executable = collections.namedtuple("Executable", "lib,source_file,build_dir,output,build_command,build_spec,functions")

class Executable(_Executable):

    def compute_built_filename(self, filename):
        return os.path.join(self.build_dir, filename)

    def extract_build_name(self, filename):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

    def get_default_function_name(self):
        if len(self.functions) == 1:
            return list(self.functions.values())[0].name
        else:
            raise ValueError(f"There's is not exactly one function ({list(self.functions.keys())}), so you need to provide one.")


class Builder:
    
    def __init__(self, build_spec, build_root=None, parser=None, result_factory=None):
        self.build_spec = build_spec
        self.source_file = build_spec.source_file
        self.result_factory = result_factory or Executable
        self.parser = parser or CProtoParser()
        self.source_name_base = self._compute_source_name_base()
        self.build_parameters = build_spec.build_parameters

        self._raise_on_invalid_parameters()

        self.build_root = build_root

        if self.build_root is None:
            self.build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")

        self.build_directory = self._compute_build_directory()

        
    def build(self):
        raise NotImplemented

    
    def _compute_build_directory(self):
        return os.path.join(self.build_root, "__".join([f"{p}_{v.replace(' ', '')}" for p,v in self.build_parameters.items()]) + "_" + self.source_name_base)

    
    def _compute_source_name_base(self):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

    
    def _raise_on_invalid_parameters(self):
        for k,v in self.build_parameters.items():
            if not any([isinstance(v, t) for t in [int, str, float]]) or isinstance(v, bool): # bool is an int!
                raise ValueError(f"Can't have '{v}' as parameter value.")
            if not isinstance(k, str):
                raise ValueError(f"Parameter names must be strings (not {k}).")
            

class BuildFailure(Exception):
    def __str__(self):
        return f"Build command failed:\n\n{self.args[0]}\n\n{self.args[1]}"
    
class BadBuildParameter(Exception):
    pass
