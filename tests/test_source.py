from fiddle.MakeBuilder import MakeBuilder
from fiddle.Builder import ExecutableDescription, Executable
from fiddle.source import *


def test_source():

    build = MakeBuilder(build_spec=ExecutableDescription("test_src/test.cpp", build_parameters={}),
                        rebuild=True,
                        verbose=True)
    
    test = build.build()
    assert isinstance(test, FullyInstrumentedExecutable)
    
    with open("test_src/test.cpp") as f:
        f = f.read()
    assert f == test.source()
    
    assert test.source(show="nop") == """int nop() {\n	return 4;\n}"""
    assert test.source(show=("//HERE", "//THERE")) == """//HERE\n//aoeu\n//THERE"""

    print(test.source(show="more", include_header=True))
    print(test.source(show="more"))
    
    assert test.source(show="more") == source_for_more

    assert test.source(show=(0,3)) == """// 0
// 1
// 2"""

    with pytest.raises(ValueError):
        test.source(show=("AOEU", "AOEU"))
    
def  test_preprocessed():

    build = MakeBuilder(build_spec=ExecutableDescription("test_src/test.cpp", build_parameters={}),
                        rebuild=True,
                        verbose=True)
    test = build.build()
    
    with pytest.raises(ValueError):
        test.preprocessed(show="more")

def _test_asm():
    # for some reason this hangs on asm(), yet asm() works fine in real code.
    from .MakeBuilder import MakeBuilder

    build = MakeBuilder()
    build.rebuild()
    build.register_analysis(asm)
    
    test = build("test_src/test.cpp")
    nop_asm = test.asm(show="nop")
    assert nop_asm.split("\n")[0] == "nop:"
    assert ".cfi_endproc" in nop_asm.split("\n")[-1]


def test_CPP_flags():

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


