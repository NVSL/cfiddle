import re
import os
import subprocess
import pytest

def asm(build_result, show=None, demangle=True, **kwargs):
    source_base_name = build_result.extract_build_name(build_result.source_file)
    asm_file = build_result.compute_built_filename(f"{source_base_name}.s")

    with open(asm_file) as f:
        if demangle:
            asm_content = subprocess.check_output('c++filt', stdin=f).decode()
        else:
            asm_content = f.read()

    code_segment = extract_code(asm_file, asm_content, "gas", show=show, **kwargs)

    return code_segment


def source(build_result, show=None, preprocessed=False,  **kwargs):

    source_base_name = build_result.extract_build_name(build_result.source_file)

    source_file = build_result.compute_built_filename(f"{source_base_name}.ii") if preprocessed else build_result.source_file
    
    with open(source_file) as f:
        content = f.read()

    suffixes_to_language = {".CPP" : "c++",
                            ".cpp" : "c++",
                            ".cc" : "c++",
                            ".cp" : "c++",
                            ".c++" : "c++",
                            ".C" : "c++",
                            ".ii" : "c++",
                            ".c" : "c",
                            ".i" : "c"}

    _, ext = os.path.splitext(source_file)
    code_segment = extract_code(source_file, content, suffixes_to_language[ext], show=show, **kwargs)

    return code_segment
    


def extract_code(filename, contents, language, show=None, include_header=True):

    lines = contents.split("\n")
    
    if show is None:
        show = 0, len(lines)

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
        comments_syntaxes = {"c++": ("// ", ""),
                             "gas": ("; ", ""),
                             "c": ("/* ", " */")}
        
        c = comments_syntaxes[language]
        
        src = f"{c[0]}{filename}:{start_line+1}-{end_line} ({end_line-start_line} lines){c[1]}\n" + src

    return src

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
    
    test = build("test_src/test.cpp")

    with open("test_src/test.cpp") as f:
        f = f.read()
    assert f == test.source(include_header=False)
    
    assert test.source(show="nop", include_header=False) == """int nop() {\n	return 4;\n}"""
    assert test.source(show=("//HERE", "//THERE"), include_header=False) == """//HERE\n//aoeu\n//THERE"""

    source_for_more = r"""void more() {
	std::cout << "more\n";
}"""

    print(test.source(show="more", include_header=False))
    
    assert test.source(show="more", include_header=False) == source_for_more

    assert test.source(show=(0,3), include_header=False) == """// 0
// 1
// 2"""
    
    with pytest.raises(ValueError):
        test.source(preprocessed=True, include_header=False, show="more")
    with pytest.raises(ValueError):
        test.source(show=("AOEU", "AOEU"))
    
    nop_asm = test.asm(show="nop", include_header=False)
    assert nop_asm.split("\n")[0] == "nop:"
    assert ".cfi_endproc" in nop_asm.split("\n")[-1]

    test_with_more = build("test_src/test.cpp", MORE_CXXFLAGS="-DINCLUDE_MORE")[0]

    def strip_whitespace(text):
        return "\n".join([l.strip() for l in text])
    
    assert strip_whitespace(test_with_more.source(preprocessed=True, include_header=False, show="more")) == strip_whitespace(source_for_more)
    
