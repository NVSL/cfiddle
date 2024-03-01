from cfiddle import *
from util import *
from fixtures import *
from cfiddle.jupyter import *
from cfiddle.jupyter.util import *
import cfiddle.jupyter.source
import IPython
from cfiddle.config import cfiddle_config
from IPython.display import SVG, HTML, TextDisplayObject, Code
import os

def test_jupyter(setup):
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build("test_src/test.cpp")[0]
        assert isinstance(test_cpp, cfiddle.jupyter.source.InstrumentedExecutable)
        assert isinstance(test_cpp.asm(), Code)
        assert isinstance(test_cpp.source(), Code)
        assert isinstance(test_cpp.preprocessed(), Code)
        assert isinstance(test_cpp.debug_info(), str)
        assert isinstance(test_cpp.cfg("sum"), HTML)
        assert os.path.exists(os.path.join(test_cpp.build_dir, "sum.svg"))

def test_raw_output_in_jupyter(setup):
    test_cpp_outside = build("test_src/test.cpp")[0]
    
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build("test_src/test.cpp")[0]
        assert test_cpp.raw_preprocessed() == test_cpp_outside.preprocessed()
        assert test_cpp.raw_asm() == test_cpp_outside.asm()
        assert test_cpp.raw_source() == test_cpp_outside.source()
        

def test_compare(setup):
    with cfiddle_config():
        configure_for_jupyter()
        test_cpp = build("test_src/test.cpp")[0]
        assert isinstance(compare([test_cpp.cfg("sum"), test_cpp.cfg("sum"), "AOEU"]), HTML)
    

def test_exceptions(setup):
    with cfiddle_config(ExceptionHandler_type=PrettyExceptionHandler):
        configure_for_jupyter()
        build(code("aoeu"))

def test_build_exception(setup):
    with cfiddle_config(ExceptionHandler_type=PrettyExceptionHandler):
        configure_for_jupyter()
        build(code("aoeu"), arg_map(a=1))

def test_run_exception(setup):
    with cfiddle_config(ExceptionHandler_type=PrettyExceptionHandler):
        configure_for_jupyter()
        run(build(code(r"""
                       extern "C"
                       int foo()  
                       {return *(int*)(0);}""")), 'foo')
