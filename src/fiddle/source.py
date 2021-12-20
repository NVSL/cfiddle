import re
import os
import subprocess
import pytest

from .Builder import Executable

class Source:
    
    def source(self, show=None, language=None, **kwargs):
        if language is None:
            language = infer_language(self.build_spec.source_file)
        return extract_code(self.build_spec.source_file, show=show, language=language, **kwargs)


class Assembly:

    def asm(self, show=None, demangle=True, **kwargs):
        source_base_name = self.extract_build_name(self.build_spec.source_file)
        asm_file = self.compute_built_filename(f"{source_base_name}.s")

        with open(asm_file) as f:
            assembly = f.read()

        assembly = self.demangle_assembly(assembly) if demangle else assembly

        return extract_code(asm_file, show=show, language="gas", **kwargs)

    
    def demangle_assembly(self, assembly):
        p = subprocess.Popen(['c++filt'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        output, output_err = p.communicate(assembly)
        return output.decode()


class Preprocessed:

    def preprocessed(self, show=None, language=None,  **kwargs):
        if language is None:
            language = infer_language(self.build_spec.source_file)

        compiled_source_base_name = self.extract_build_name(self.build_spec.source_file)
        preprocessed_suffix = self.compute_preprocessed_suffix(self.build_spec.source_file, language=language)
        source_file_to_search = self.compute_built_filename(f"{compiled_source_base_name}{preprocessed_suffix}")

        return extract_code(source_file_to_search, show=show, language=language, **kwargs)

    def compute_preprocessed_suffix(self, filename, language):
        if language is None:
            language = infer_language(filename)

        if language == "c++":
            return ".ii"
        elif language == "c":
            return ".i"
        else:
            raise ValueError(f"Can't compute preprocessor file extension for file  '{filename}' in '{language}'.")

        
class FullyInstrumentedExecutable(Preprocessed, Source, Assembly, Executable):
    def __init__(self, *argc, **kwargs):
        super().__init__(*argc, **kwargs)


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
        return (fr"[\s\*]{re.escape(function)}\s*\(", r"^\}")
    elif language == "gas":
        return (fr"^{re.escape(function)}:\s*", ".cfi_endproc")
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

    
