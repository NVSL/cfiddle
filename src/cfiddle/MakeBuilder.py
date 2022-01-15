from .Builder import Builder, Executable, BadBuildParameter, BuildFailure
import os
import subprocess
import pytest
from shutil import copyfile
from .util import environment, invoke_process

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
        
        so_make_target = self._compute_so_make_target(self.build_directory)
        so_unique_name = self._compute_so_unique_name(self.build_directory)

        vpath = ":".join([os.path.dirname(self.source_file), self.build_directory])

        parameter_strings  = [f"{name}={value}" for name, value in self.build_parameters.items()]
        parameter_strings += [f"BUILD={self.build_directory}"]
        parameter_strings += [f"CFIDDLE_INCLUDE={os.path.join(DATA_PATH, 'include')}"]
        parameter_strings += [f"CFIDDLE_VPATH={vpath}"]
        
        base_cmd = ["make", "-f", self._makefile] + parameter_strings
        
        if self._rebuild:
            make_targets = ["clean"]
        else:
            make_targets = []
            
        make_targets.append(so_make_target)

        if self._verbose:
            print(base_cmd + make_targets)
        output = self._invoke_make(base_cmd + make_targets)
        if self._verbose:
            print(output)

        copyfile(so_make_target, so_unique_name)

        functions = self.parser.parse_file(self.source_file)


        return self.result_factory(lib=so_unique_name,
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
