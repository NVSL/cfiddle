from cfiddle import *
from util import *
from fixtures import *
from cfiddle.source import InstrumentedExecutable, InspectionError, Assembly
import pytest
import re

def test_source(test_cpp):
    
    assert isinstance(test_cpp, InstrumentedExecutable)
    
    with open("test_src/test.cpp") as f:
        f = f.read()
    assert f == test_cpp.source()
    
    assert test_cpp.source(show="nop") == """int nop() {\n	return 4;\n}"""
    assert test_cpp.source(show=("//HERE", "//THERE")) == """//HERE\n//aoeu\n//THERE"""
    
    print(test_cpp.source(show="more", include_header=True))
    print(test_cpp.source(show="more"))
    
    assert test_cpp.source(show="more") == source_for_more

    assert test_cpp.source(show=(0,3)) == """// 0
// 1
// 2"""

    with pytest.raises(InspectionError):
        test_cpp.source(show=("AOEU", "AOEU"))

        
def  test_preprocessed(test_cpp):
    with pytest.raises(InspectionError):
        test_cpp.preprocessed(show="more")

def test_asm(test_cpp):
    asm = test_cpp.asm(show="nop")
    assert asm.split("\n")[0] == "nop:"
    assert ".cfi_endproc" in asm.split("\n")[-1]

def test_filter(test_cpp):
    asm = test_cpp.asm(filter="^nop:")
    assert len(asm.split("\n")) == 1
    asm = test_cpp.asm(filter="^[^\.\s]\w.*:")
    assert len(asm.split("\n")) == 10
    asm = test_cpp.asm(demangle=False, filter="^[^\.\s]\w.*:")
    assert len(asm.split("\n")) == 10

    asm = test_cpp.asm(demangle=False, filter=Assembly.FUNCTION_LABEL)
    assert len(asm.split("\n")) == 10

    asm = test_cpp.asm(demangle=False, filter=lambda x : re.search("^[^\.\s]\w.*:",x))
    assert len(asm.split("\n")) == 10
    
def test_demangle(test_cpp):
    not_demangled = test_cpp.asm(demangle=False)
    assert "_Z11demangle_mev" in not_demangled
    assert "demangle_me():" not in not_demangled
    
    demangled = test_cpp.asm()
    assert "_Z11demangle_mev" not in demangled
    with open("t", "w") as t:
        t.write(demangled)
    assert "demangle_me():" in demangled

def test_CPP_flags(setup):

    build = MakeBuilder(build_spec=ExecutableDescription("test_src/test.cpp", build_parameters=dict(MORE_CXXFLAGS="-DINCLUDE_MORE")),
                        rebuild=True,
                        verbose=True)
    test = build.build()

    def strip_whitespace(text):
        return "\n".join([l.strip() for l in text])
    
    assert strip_whitespace(test.preprocessed(include_header=False, show="more")) == strip_whitespace(source_for_more)


source_for_more = r"""void more() {
	std::cout << "more\n";
}"""


