import collections
from .CProtoParser import CProtoParser
from .util import expand_args, read_file
import types
import os
import hashlib
import pytest

            
class BuildFailure(Exception):
    def __str__(self):
        return f"Build command failed:\n\n{self.args[0]}\n\n{self.args[1]}"
    
class BadBuildParameter(Exception):
    pass

_BuildResult = collections.namedtuple("BuildResult", "lib,source_file,build_dir,output,build_command,parameters,functions")

class BuildResult(_BuildResult):

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
            raise ValueError(f"There's is not exactly one function ({list(build_result.functions.keys())}), so you need to provide one.")
    

class Builder:
    
    def __init__(self, parser=None, build_root=None):
        self.parser = parser or CProtoParser()
        self.analyses = {}
        self.build_root = build_root
        if self.build_root is None:
            self.build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")
        
    def build_one(self, source_file, parameters=None):
        raise NotImplemented

    def build(self, source_file=None, parameters=None, code=None, **kwargs):

        if source_file is None:
            if code is None:
                raise ValueError("You must provide either a source_file or code")
            source_file = self._write_anonymous_source(code)
            
        if isinstance(source_file, BuildResult):
            source_file = source_file.source_file
        
        if code:
            self._update_source(source_file, code)

        if isinstance(parameters, list):
            singleton = False
        else:
            singleton = None
            
        if parameters is None:
            parameters = [] if kwargs else {}
            
        if isinstance(parameters, dict):
            parameters = [parameters]
        if kwargs:
            parameters += expand_args(**kwargs)

        if singleton is None:
            singleton = len(parameters) == 1

        self._raise_on_invalid_parameters(parameters)
        
        r = ListDelegator(self._add_analysis_functions(self.build_one(source_file, p)) for p in parameters)
        return r[0] if singleton else r

    
    def __call__(self, *argc, **kwargs):
        return self.build(*argc, **kwargs)

    def _raise_on_invalid_parameters(self, parameters):
        for p in parameters:
            for k,v in p.items():
                if v is None:
                    raise ValueError("Can't have 'None' as parameter value in {p}")
    
    def _add_analysis_functions(self, result):
        for a in self.analyses:
            setattr(result, a, types.MethodType(self.analyses[a], result))
        return result

    
    def _update_source(self, source_file, source):
        with open(source_file) as r:
            contents = r.read()
        if contents != source:
            with open(source_file, "w") as r:
                r.write(source)

                
    def _write_anonymous_source(self, code):
        hash_value = hashlib.md5(code.encode('utf-8')).hexdigest()
        anonymous_source_path = os.path.join(self.build_root, f"{hash_value}.cpp")
        with open(anonymous_source_path, "w") as f:
            f.write(code)
        return anonymous_source_path

    
    def _compute_build_directory(self, source_file, parameters):
        _, source_name = os.path.split(source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return os.path.join(self.build_root, "__".join([f"{p}_{v}" for p,v in parameters.items()]) + "_" + source_name_base)


    def register_analysis(self, analysis, as_name=None):
        if as_name is None:
            as_name = analysis.__name__
        self.analyses[as_name] = analysis
        return self

    
class CompiledFunctionDelegator:
    def __init__(self, build_result, function_name=None):
        self.build_result = build_result
        if function_name is None:
            function_name = build_result.get_default_function_name()

        self.function_name = function_name

    def __getattr__(self, name):
        attr = getattr(self.build_result, name)
        if callable(attr):
            def redirect_to_build_result(*args, **kwargs):
                return attr(self.function_name, *args, **kwargs)
            return redirect_to_build_result
        else:
            return attr

class NopBuilder(Builder):
    
    def build_one(self, source_path, parameters):
        _, source_file = os.path.split(source_path)
        source_file_base, _ = os.path.splitext(source_file)
        build_directory = self._compute_build_directory(source_file, parameters)
        return BuildResult(f"{source_file}.so", source_path, build_directory, "no output", str(parameters), parameters, {f"{source_file_base}_func": "nonsense_value"})
    
def test_builder():

    simple_singleton = NopBuilder().build("test_src/test.cpp")
    assert isinstance(simple_singleton, BuildResult)
    assert simple_singleton.parameters == {}

    parameters = dict(foo="bar")

    singleton = NopBuilder().build("test_src/test.cpp", parameters)
    assert isinstance(singleton, BuildResult)
    assert singleton.parameters == parameters

    single_item_list = NopBuilder().build("test_src/test.cpp", parameters=[parameters])
    assert isinstance(single_item_list, list)
    assert len(single_item_list) == 1

    empty_list = NopBuilder().build("test_src/test.cpp", parameters=[])
    assert isinstance(empty_list, list)
    assert len(empty_list) == 0

    kwargs_singleton = NopBuilder().build("test_src/test.cpp", **parameters)
    assert isinstance(kwargs_singleton, BuildResult)
    assert kwargs_singleton.parameters == parameters

    short_list = NopBuilder().build("test_src/test.cpp", [parameters])
    assert isinstance(short_list, list)
    assert len(short_list) == 1
    assert short_list[0].parameters == parameters

    kwargs_list = NopBuilder().build("test_src/test.cpp", foo=["bar","baz"], bar="foo")
    assert isinstance(kwargs_list, list)
    assert len(kwargs_list) == 2
    assert all([isinstance(x, BuildResult) for x in kwargs_list])
    assert kwargs_list[0].parameters == dict(foo="bar", bar="foo")
    assert kwargs_list[1].parameters == dict(foo="baz", bar="foo")
    
    compound_list = NopBuilder()("test_src/test.cpp", parameters=[parameters, dict(b="c")], foo=["bar","baz"], bar="foo")
    assert isinstance(compound_list, list)
    assert len(compound_list) == 4
    assert all([isinstance(x, BuildResult) for x in compound_list])
    assert compound_list[0].parameters == parameters

    embedded_code = NopBuilder().build(code="somecode")
    assert os.path.exists(embedded_code.source_file)
    assert read_file(embedded_code.source_file) == "somecode"

def test_invalid_parameters():
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=None)
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=[None, ""])
    
def test_decoration():
    
    def get_parameters(build_result):
        return build_result.parameters

    def get_one_parameter(build_result, parameter):
        return build_result.parameters[parameter]

    build = NopBuilder()
    build.register_analysis(get_parameters)
    build.register_analysis(get_one_parameter)

    parameters = dict(foo="bar")
    singleton = build("test_src/test.cpp", parameters)
    assert singleton.get_parameters() == parameters
    assert singleton.get_one_parameter("foo") == "bar"

    
def test_delegator():
    build = NopBuilder()
    build.register_analysis(CompiledFunctionDelegator, as_name="function")
    def return_function(build_result, function_name):
        return build_result.functions[function_name]
    build.register_analysis(return_function)
    simple_singleton = build.build("test_src/test.cpp")

    delegated_function = simple_singleton.function("test_func")

    assert delegated_function.parameters == simple_singleton.parameters
    assert simple_singleton.functions["test_func"] == "nonsense_value"
    assert delegated_function.return_function() == "nonsense_value"

def test_foo():
    from .MakeBuilder import MakeBuilder
    build = MakeBuilder()
    build.register_analysis(CompiledFunctionDelegator, as_name="function")


    if_ex = build(code=r"""
#include<cstdint>
#include<cstdlib>

extern "C" 
int if_ex(uint64_t array, unsigned long int size) {
	if (size == 0) {
		return NULL;
	}
	return array+size;
}
""")

    if_ex = if_ex.function()
