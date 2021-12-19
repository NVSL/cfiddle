import pytest

from fiddle import *


@pytest.mark.skip(reason="no way of currently testing this")
def test_builder():

    simple_singleton = NopBuilder().build("test_src/test.cpp")
    assert isinstance(simple_singleton, Executable)
    assert simple_singleton.parameters == {}

    parameters = dict(foo="bar")

    singleton = NopBuilder().build("test_src/test.cpp", parameters)
    assert isinstance(singleton, Executable)
    assert singleton.parameters == parameters

    single_item_list = NopBuilder().build("test_src/test.cpp", parameters=[parameters])
    assert isinstance(single_item_list, list)
    assert len(single_item_list) == 1

    empty_list = NopBuilder().build("test_src/test.cpp", parameters=[])
    assert isinstance(empty_list, list)
    assert len(empty_list) == 0

    kwargs_singleton = NopBuilder().build("test_src/test.cpp", **parameters)
    assert isinstance(kwargs_singleton, Executable)
    assert kwargs_singleton.parameters == parameters

    short_list = NopBuilder().build("test_src/test.cpp", [parameters])
    assert isinstance(short_list, list)
    assert len(short_list) == 1
    assert short_list[0].parameters == parameters

    kwargs_list = NopBuilder().build("test_src/test.cpp", foo=["bar","baz"], bar="foo")
    assert isinstance(kwargs_list, list)
    assert len(kwargs_list) == 2
    assert all([isinstance(x, Executable) for x in kwargs_list])
    assert kwargs_list[0].parameters == dict(foo="bar", bar="foo")
    assert kwargs_list[1].parameters == dict(foo="baz", bar="foo")
    
    compound_list = NopBuilder()("test_src/test.cpp", parameters=[parameters, dict(b="c")], foo=["bar","baz"], bar="foo")
    assert isinstance(compound_list, list)
    assert len(compound_list) == 4
    assert all([isinstance(x, Executable) for x in compound_list])
    assert compound_list[0].parameters == parameters

    embedded_code = NopBuilder().build(code="somecode")
    assert os.path.exists(embedded_code.source_file)
    assert read_file(embedded_code.source_file) == "somecode"

    
def test_invalid_parameters():
    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=None))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=True))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE=[]))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", dict(OPTIMIZE={}))

    with pytest.raises(ValueError):
        build("test_src/test.cpp", {4:""})

        
    
@pytest.mark.skip(reason="no way of currently testing this")
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

    
def _test_code():
    build_and_run(code(r"""
extern "C" 
int four() {
    return 4;
}
"""), {}, "four", {})
    


