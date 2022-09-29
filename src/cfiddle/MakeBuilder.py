from .Builder import Builder, InvalidBuildParameter, BuildFailure
import os
import subprocess
import pytest
from shutil import copyfile
from .util import environment, invoke_process
from .Toolchain import TheToolchainRegistry

import pkg_resources

DATA_PATH = pkg_resources.resource_filename('cfiddle', 'resources/')

class MakeBuilder(Builder):

    def __init__(self,
                 *argc,
                 **kwargs
                 ):
        self._makefile = kwargs.pop("makefile",os.path.join(DATA_PATH, "make", "cfiddle.make"))
        self._rebuild = kwargs.pop("rebuild", False)
        self._verbose = kwargs.pop("verbose", False)

        super().__init__(*argc, **kwargs)


    def build(self):
        self.toolchain = self._resolve_toolchain()
        
        so_make_target = self._compute_so_make_target(self.build_directory)
        so_unique_name = self._compute_so_unique_name(self.build_directory)

        vpath = ":".join([os.path.dirname(self.source_file), self.build_directory])

        parameter_strings  = [f"{name}={value}" for name, value in self.build_parameters.items()]
        parameter_strings += [f"BUILD={self.build_directory}"]
        parameter_strings += [f"CFIDDLE_INCLUDE={os.path.join(DATA_PATH, 'include')}"]
        parameter_strings += [f"CFIDDLE_VPATH={vpath}"]
        #parameter_strings += [f"COMPILER={self.toolchain.get_compiler()}"]
        parameter_strings += [f"TARGET={self.toolchain.get_target()}"]
        
        base_cmd = ["make",
                    "-R", # turn off automatic variables
                    "-f", self._makefile] + parameter_strings
        
        if self._rebuild:
            make_targets = ["clean"]
        else:
            make_targets = []
            
        make_targets.append(so_make_target)

        if self._verbose:
            print(base_cmd + make_targets)
            print(" ".join(base_cmd + make_targets))
        output = self._invoke_make(base_cmd + make_targets)
        if self._verbose:
            print(output)

        copyfile(so_make_target, so_unique_name)

        functions = self.parser.parse_file(self.source_file)

        extra_source = self._collect_extra_source()

        for e in extra_source:
            functions.update(self.parser.parse_file(e))
            
        return self.result_factory(lib=so_unique_name,
                                   toolchain=self.toolchain,
                                   functions=functions,
                                   build_command=self._build_manual_make_cmd(base_cmd + make_targets),
                                   build_dir=self.build_directory,
                                   output=output,
                                   build_spec=self.build_spec)


    def rebuild(self, rebuild=True):
        self._rebuild = rebuild

        
    def makefile(self, makefile):
        self._makefile = makefile

        
    def verbose(self, verbose=True):
        self._verbose = verbose


    def _collect_extra_source(self):
        if "MORE_SRC" in self.build_parameters:
            return self.build_parameters["MORE_SRC"].split()
        else:
            return []    
        
        
    def _get_multiarch_string(self, tool):
        success, value = invoke_process([tool, "-print-multiarch"])
        if not success:
            raise ToolError(f"Couldn't extract multiarch string from {tool}")
        else:
            return value.strip()

        
    def _resolve_toolchain(self):

        default_compiler, make_var = self._default_compiler_for_language(self.build_spec.get_language())
        raw_compiler = self.build_spec.get_build_parameters().get(make_var, default_compiler)

        toolchain = TheToolchainRegistry.get_toolchain(language=self.build_spec.get_language(),
                                                       build_parameters=self.build_spec.get_build_parameters(),
                                                       tool=raw_compiler)
        
        if default_compiler != toolchain.get_compiler():
            self.build_spec.set_build_parameter(make_var, toolchain.get_compiler())

        return toolchain
    
    def _build_manual_make_cmd(self, cmd):
        return " ".join(cmd)

    
    def _invoke_make(self, cmd):
        success, output = invoke_process(cmd)
        if not success:
            raise BuildFailure(" ".join(cmd), output)
        return output

    
    def _compute_so_make_target(self, build_directory):
        return os.path.join(build_directory, f"{self.source_name_base}.so")

    
    def _compute_so_unique_name(self, build_directory):
        number = 0

        while True:
            unique_path = os.path.join(build_directory, f"{self.source_name_base}_{number}.so")
            if not os.path.exists(unique_path):
                break
            number += 1

        return unique_path

    def _default_compiler_for_language(self, language):
        if language.upper() == "C":
            return "gcc", "CC"
        elif language.upper() == "C++":
            return "g++", "CXX"
        elif language.upper() == "GO":
            return "go", "GO"
