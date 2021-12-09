import collections
from .CProtoParser import CProtoParser
from .util import expand_args


class BuildFailure(Exception):
    pass
class BadBuildParameter(Exception):
    pass

BuildResult = collections.namedtuple("BuildResult", "lib,build_dir,output,build_command,parameters,functions")

class Builder:

    def __init__(self, parser=None):
        self.parser = parser or CProtoParser()
        
    def build_one(self, source_file, parameters=None, rebuild=False, build_directory=None, build_root=None, makefile=None):
        raise NotImplemented

    def build(self, source_file, parameters=None, **kwargs):
        if parameters is None:
            parameters = {}
        if isinstance(parameters, dict):
            return self.build_one(source_file, parameters, **kwargs)
        else:
            return [self.build_one(source_file, p, **kwargs) for p in parameters]
        
    
def do_build(builder, source, **kwargs):
    return builder.build(source, parameters=expand_args(**kwargs))
