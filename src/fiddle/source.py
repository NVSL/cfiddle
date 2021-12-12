import re
import os
import subprocess

def asm(build_result, show=None, demangle=True, **kwargs):
    asm_file = build_result.compute_built_filename(f"{source_name_base}.s")

    with open(asm_file) as f:
        if demangle:
            asm_content = subprocess.check_output('c++filt', stdin=f).decode()
        else:
            asm_content = f.read()

    code_segment = extract_code(asm_file, asm_content, "gas", show=show, **kwargs)

    return code_segment


def source(build_result, preprocessed=False, show=None, **kwargs):

    source_file = build_result.compute_built_filename(f"{source_name_base}.ii") if preprocessed else build_result.source_file
    
    with open(source_file) as f:
        content = f.read()

    suffixes_to_language = {".CPP" : "c++",
                            ".cpp" : "c++",
                            ".cc" : "c++",
                            ".cp" : "c++",
                            ".c++" : "c++",
                            ".C" : "c++",
                            ".c" : "c"}

    _, ext = os.path.splitext(build_result.source_file)
    code_segment = extract_code(build_result.source_file, content, suffixes_to_language[ext], show=show, **kwargs)

    return code_segment
    
    
def extract_code(filename, contents, language, show=None, include_header=True):

    lines = contents.split("\n")
    start_line = 0
    end_line = len(lines)

    if show is None:
        show = start_line, end_line

    if isinstance(show, str):
        if language == "c++":
            show = (f"[\s\*]{re.escape(show)}\s*\(", "^\}")
        elif language == "gas":
            show = (f"^{re.escape(show)}:\s*", ".cfi_endproc")
        else:
            raise Exception(f"Don't know how to find functions in {language}")
        
    if len(show) == 2:
        if all([isinstance(x, str) for x in show]): 
            started = False
            for n, l in enumerate(lines):
                if not started:
                    if re.search(show[0], l):
                        start_line = n
                        started = True

                else:
                    if re.search(show[1], l):
                        end_line = n + 1
                        break
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


def test_extract_source():
    from .MakeBuilder import MakeBuilder

    build = MakeBuilder()
    build.register_analysis(source)
    build.register_analysis(asm)
    
    test = build("test_src/test.cpp")

    with open("test_src/test.cpp") as f:
        f = f.read()
    assert f == test.source(include_header=False)
    
    assert test.source(show="nop", include_header=False) == """int nop() {\n	return 4;\n}"""
    assert test.source(show=("//HERE", "//THERE"), include_header=False) == """//HERE\n//aoeu\n//THERE"""

    nop_asm = test.asm(show="nop", include_header=False)
    assert nop_asm.split("\n")[0] == "nop:"
    assert ".cfi_endproc" in nop_asm.split("\n")[-1]


    


