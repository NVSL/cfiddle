import os

from cfiddle import *
from cfiddle.Code import SourceCodeModified
from util import *
from cfiddle.config import get_config
from cfiddle.util import read_file, write_file, working_directory

from fixtures import *

def test_code_cpp(setup):
    build_and_run(code(r"""
    extern "C" 
        int four() {
    return 4;
    }
"""), {}, "four", {})
    assert os.path.exists(os.path.join(get_config("CFIDDLE_BUILD_ROOT"), "anonymous_code"))


def test_explicit_cpp(setup):
    build_and_run(code(r"""
    extern "C" 
        int four() {
    return 4;
    }
""", language="c++"), {}, "four", {})


def test_code_c(setup):
    build_and_run(code(r"""
    int four() {
        return 4;
    }
    """, language="c"), {}, "four", {})

    
def test_modification(setup):
    s = r"""aoeu"""
    f = code(s)
    f = code(s + "hello", f) # write different code
    f = code(s, f) # write the original code
    written = read_file(f).split("\n")

    write_file(f, "\n".join(["t"] + written)) # append
    with pytest.raises(SourceCodeModified):
        code(s, file_name=f)

    write_file(f, "\n".join(["t"] + written[1:])) # remove first line
    with pytest.raises(SourceCodeModified):
        code(s, file_name=f)

    write_file(f, "\n".join(written[:-1])) # remove signature line
    with pytest.raises(SourceCodeModified):
        code(s, file_name=f)
    

def test_code_file(setup):
    with tempfile.TemporaryDirectory() as d:
        with working_directory(d):
            for file_name in ["foo.cpp", os.path.join(d, "bar.cpp")]:
                source = r"""
                int four() {
                return 4;
                }
                """
                actual_name = code(source, file_name=file_name, language="cpp", raw=True)
                assert os.path.exists(actual_name)
                assert actual_name == file_name
                assert read_file(actual_name) == source

