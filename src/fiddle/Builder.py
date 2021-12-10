import collections
from .CProtoParser import CProtoParser
from .util import expand_args
import types

class BuildFailure(Exception):
    pass
class BadBuildParameter(Exception):
    pass

_BuildResult = collections.namedtuple("BuildResult", "lib,build_dir,output,build_command,parameters,functions")

class BuildResult(_BuildResult):
    pass

class Builder:
    
    def __init__(self, parser=None):
        self.parser = parser or CProtoParser()
        self.analyses = {}

    def _decorate_result(self, result):
        for a in self.analyses:
            setattr(result, a, types.MethodType(self.analyses[a], result))
        return result
    
    def build_one(self, source_file, parameters=None, rebuild=False, build_directory=None, build_root=None, makefile=None):
        raise NotImplemented

    def build(self, source_file, parameters=None, rebuild=False, build_directory=None, build_root=None, makefile=None, **kwargs):
        if parameters is None and not kwargs:
            parameters = {}
        elif parameters is None:
            parameters = expand_args(**kwargs)
            
        if isinstance(parameters, dict):
            return self._decorate_result(self.build_one(source_file, parameters, rebuild=rebuild, build_directory=build_directory, build_root=build_root, makefile=makefile))
        else:
            return [self._decorate_result(self.build_one(source_file, p, rebuild=rebuild, build_directory=build_directory, build_root=build_root, makefile=makefile)) for p in parameters]

    def __call__(self, *argc, **kwargs):
        return self.build(*argc, **kwargs)

    def register_analysis(self, analysis):
        """
        Add an analysis function to the BuildResults returned by the builder.  It'll be added as a method for the `BuildResult`s, 
        so it should take a `BuildResult` as the first argument.
        """
        self.analyses[analysis.__name__] = analysis
        return self
        

