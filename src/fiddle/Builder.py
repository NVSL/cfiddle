import collections
from .CProtoParser import CProtoParser
from .util import expand_args
import types

class BuildFailure(Exception):
    pass
class BadBuildParameter(Exception):
    pass

_BuildResult = collections.namedtuple("BuildResult", "lib,source_file,build_dir,output,build_command,parameters,functions")

class BuildResult(_BuildResult):

    def compute_built_filename(self, filename):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return os.path.join(build_result.build_dir, filename)

class Builder:
    
    def __init__(self, parser=None):
        self.parser = parser or CProtoParser()
        self.analyses = {}
        
    def _add_analysis_functions(self, result):
        for a in self.analyses:
            setattr(result, a, types.MethodType(self.analyses[a], result))
        return result
    
    def build_one(self, source_file, parameters=None):
        raise NotImplemented

    def build(self, source_file, parameters=None, **kwargs):

        if parameters is None:
            parameters = [] if kwargs else {}
            
        singleton = False            
        if isinstance(parameters, dict):
            parameters = [parameters]
            singleton = True
        if kwargs:
            parameters += expand_args(**kwargs)
            singleton = False

        r = [self._add_analysis_functions(self.build_one(source_file, p)) for p in parameters]
        return r[0] if singleton else r

    def __call__(self, *argc, **kwargs):
        return self.build(*argc, **kwargs)

    def register_analysis(self, analysis):
        """
        Add an analysis function to the BuildResults returned by the builder.  It'll be added as a method for the `BuildResult`s, 
        so it should take a `BuildResult` as the first argument.
        """
        self.analyses[analysis.__name__] = analysis
        return self
    
class TestBuilder(Builder):
    
    def build_one(self, source_file, parameters):
        return BuildResult(f"{source_file}.so", source_file, f"dir_{source_file}", "no output", str(parameters), parameters, {})
    
def test_builder():

    simple_singleton = TestBuilder().build("foo.cpp")
    assert isinstance(simple_singleton, BuildResult)
    assert simple_singleton.parameters == {}

    parameters = dict(foo="bar")

    singleton = TestBuilder().build("foo.cpp", parameters)
    assert isinstance(singleton, BuildResult)
    assert singleton.parameters == parameters
    
    short_list = TestBuilder().build("foo.cpp", [parameters])
    assert isinstance(short_list, list)
    assert len(short_list) == 1
    assert short_list[0].parameters == parameters

    kwargs_list = TestBuilder().build("foo.cpp", foo=["bar","baz"], bar="foo")
    assert isinstance(kwargs_list, list)
    assert len(kwargs_list) == 2
    assert all([isinstance(x, BuildResult) for x in kwargs_list])
    assert kwargs_list[0].parameters == dict(foo="bar", bar="foo")
    assert kwargs_list[1].parameters == dict(foo="baz", bar="foo")
    
    compound_list = TestBuilder()("foo.cpp", parameters=[parameters, dict(b="c")], foo=["bar","baz"], bar="foo")
    assert isinstance(compound_list, list)
    assert len(compound_list) == 4
    assert all([isinstance(x, BuildResult) for x in compound_list])
    assert compound_list[0].parameters == parameters
    
def test_decoration():
    
    def get_parameters(build_result):
        return build_result.parameters

    def get_one_parameter(build_result, parameter):
        return build_result.parameters[parameter]

    build = TestBuilder()
    build.register_analysis(get_parameters)
    build.register_analysis(get_one_parameter)

    parameters = dict(foo="bar")
    singleton = build("foo.cpp", parameters)
    assert singleton.get_parameters() == parameters
    assert singleton.get_one_parameter("foo") == "bar"

