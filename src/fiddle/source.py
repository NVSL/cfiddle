import re
import os
import subprocess
import pytest


def source(build_result, show=None, language=None, **kwargs):
    if language is None:
        language = infer_language(build_result.source_file)
    return extract_code(build_result.source_file, show=show, language=language, **kwargs)


def asm(build_result, show=None, demangle=True, **kwargs):
    source_base_name = build_result.extract_build_name(build_result.source_file)
    asm_file = build_result.compute_built_filename(f"{source_base_name}.s")

    with open(asm_file) as f:
        assembly = f.read()

    assembly = demangle_assembly(assembly) if demangle else assembly

    return extract_code(asm_file, show=show, language="gas", **kwargs)


def preprocessed(build_result, show=None, language=None,  **kwargs):
    if language is None:
        language = infer_language(build_result.source_file)
        
    compiled_source_base_name = build_result.extract_build_name(build_result.source_file)
    preprocessed_suffix = compute_preprocessed_suffix(build_result.source_file, language=language)
    source_file_to_search = build_result.compute_built_filename(f"{compiled_source_base_name}{preprocessed_suffix}")
    
    return extract_code(source_file_to_search, show=show, language=language, **kwargs)


def compute_preprocessed_suffix(filename, language):
    if language is None:
        language = infer_language(filename)

    if language == "c++":
        return ".ii"
    elif language == "c":
        return ".i"
    else:
        raise ValueError(f"Can't compute preprocessor file extension for file  '{filename}' in '{language}'.")

    
def infer_language(filename):
    suffixes_to_language = {".CPP" : "c++",
                            ".cpp" : "c++",
                            ".cc" : "c++",
                            ".cp" : "c++",
                            ".c++" : "c++",
                            ".C" : "c++",
                            ".ii" : "c++",
                            ".c" : "c",
                            ".i" : "c"}

    _, ext = os.path.splitext(filename)
    try:
        return suffixes_to_language[ext]
    except KeyError:
        raise ValueError(f"I don't know what language {filename} is written in.")

    
def extract_code(filename, show=None, language=None, include_header=False):

    with open(filename) as f:
        lines = f.read().split("\n")

    if show is None:
        show = 0, len(lines)

    if language is None:
        language = infer_language(filename)
        
    if isinstance(show, str):
        show = construct_function_regex(language, show)
        
    if len(show) == 2:
        if all([isinstance(x, str) for x in show]): 
            start_line, end_line = find_region_by_regex(lines, show)
        elif all([isinstance(x, int) for x in show]): 
            start_line, end_line = show
        else:
            raise ValueError(f"{show} is not a valid specification of code to extract.")
    else:
        raise ValueError(f"{show} is not a valid specification of code to extract.")
    
    src = "\n".join(lines[start_line:end_line])

    if include_header:
        src = build_header(filename, language,(start_line, end_line)) + src

    return src


def demangle_assembly(assembly):
    p = subprocess.Popen(['c++filt'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output, output_err = p.communicate(assembly)
    return output.decode()


def build_header(filename, language, show):
    comments_syntaxes = {"c++": ("// ", ""),
                         "gas": ("; ", ""),
                         "c": ("/* ", " */")}

    try:
        c = comments_syntaxes[language]
    except KeyError:
        raise ValueError(f"Unknown comment syntax for language '{language}'.")

    return f"{c[0]}{filename}:{show[0]+1}-{show[1]} ({show[1] - show[0]} lines){c[1]}\n"


def construct_function_regex(language, function):
    if language == "c++":
        return (f"[\s\*]{re.escape(function)}\s*\(", "^\}")
    elif language == "gas":
        return (f"^{re.escape(function)}:\s*", ".cfi_endproc")
    else:
        raise Exception(f"Don't know how to find functions in {language}")

    
def find_region_by_regex(lines, show):
    started = False
    start_line = 0
    end_line = len(lines)
    for n, l in enumerate(lines):
        if not started:
            if re.search(show[0], l):
                start_line = n
                started = True
        else:
            if re.search(show[1], l):
                end_line = n + 1
                return start_line, end_line
    raise ValueError(f"Couldn't find code for {show}")



def test_extract_source():
    from .MakeBuilder import MakeBuilder

    build = MakeBuilder()
    build.rebuild()
    build.register_analysis(source)
    build.register_analysis(asm)
    build.register_analysis(preprocessed)
    
    test = build("test_src/test.cpp")

    with open("test_src/test.cpp") as f:
        f = f.read()
    assert f == test.source()
    
    assert test.source(show="nop") == """int nop() {\n	return 4;\n}"""
    assert test.source(show=("//HERE", "//THERE")) == """//HERE\n//aoeu\n//THERE"""

    source_for_more = r"""void more() {
	std::cout << "more\n";
}"""

    print(test.source(show="more", include_header=True))
    print(test.source(show="more"))
    
    assert test.source(show="more") == source_for_more

    assert test.source(show=(0,3)) == """// 0
// 1
// 2"""
    
    with pytest.raises(ValueError):
        test.preprocessed(show="more")
    with pytest.raises(ValueError):
        test.source(show=("AOEU", "AOEU"))
    
    nop_asm = test.asm(show="nop")
    assert nop_asm.split("\n")[0] == "nop:"
    assert ".cfi_endproc" in nop_asm.split("\n")[-1]

    test_with_more = build("test_src/test.cpp", MORE_CXXFLAGS="-DINCLUDE_MORE")

    def strip_whitespace(text):
        return "\n".join([l.strip() for l in text])
    
    assert strip_whitespace(test_with_more.preprocessed(include_header=False, show="more")) == strip_whitespace(source_for_more)
    
