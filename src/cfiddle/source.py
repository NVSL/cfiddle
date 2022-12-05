import re
import os
import subprocess
import pytest
import tempfile
import io

from .Builder import Executable
from .util import invoke_process, infer_language
from .CFG.cfg import CFG
from .DebugInfo import DebugInfo
from .Exceptions import CFiddleException


class Source:
    
    def source(self, show=None, language=None, filter=None, **kwargs):
        """Return the source code for a function.
        
        This function uses regular expression-based heuristics to find the
        function, rather than actually parsing the code, this can lead to
        unexpected outputs.

        The heuristics assume that the function prototype is on a single line
        and that the function ends with a ``}`` on a line by itself.
        
        Args:
           show: What to show.  Either a function name or a 2-tuple: either ``(start_regex,end_regex)`` or ``(start_line_number,end_line_number``).  Defaults to ``None`` which shows the whole file.
           language:  What language to assume.  Defaults to ``c++``.
        Returns:
           ``str`` : The source code.

        """

        if language is None:
            language = infer_language(self.build_spec.source_file)
        return filter_code(extract_code(self.build_spec.source_file, self, show=show, language=language, **kwargs), filter)


class Assembly:

    FUNCTION_LABEL = "^[^\.\s]\w.*:"

    def asm(self, show=None, demangle=True,  filter=None,**kwargs):
        """Return the compiled assembly for a function.

        The output is from the assembly output of the compiler (e.g., the
        result of ``g++ -S``), not the compiled object code.

        This function uses regular expression-based heuristics to find the
        function, rather than actually parsing the code, this can lead to
        unexpected outputs.

        Args:
           show: What to show.  Either a function name or a 2-tuple: either ``(start_regex,end_regex)`` or ``(start_line_number,end_line_number``).  Defaults to ``None`` which shows the whole file.
           demangle: Pass the assembly through ``c++filt`` first, so C++ symbols are more readable.  Defaults to ``True``.
        Returns:
           ``str`` : The assembly.

        """
        
        source_base_name = self.extract_build_name(self.build_spec.source_file)
        asm_file = self.compute_built_filename(f"{source_base_name}.s")

        assembly = contents_of(asm_file)

        if demangle:
            assembly = self.demangle_assembly(assembly)

        return filter_code(extract_code(asm_file, self, source=assembly, show=show, language="gas", **kwargs), filter)

    
    def demangle_assembly(self, assembly):
        with tempfile.NamedTemporaryFile() as asm_file:
            asm_file.write(assembly.encode())
            asm_file.flush()

            with open(asm_file.name, "r") as f:
                success, demangled = invoke_process([self.get_toolchain().get_tool('c++filt')],
                                                    stdin=f)
            if not success:
                raise Exception("Demangling failed.")
        return demangled


class Preprocessed:

    def preprocessed(self, show=None, language=None,  filter=None, **kwargs):
        """Return the preprocessed source code for a function.

        This function uses regular expression-based heuristics to find the
        function, rather than actually parsing the code, this can lead to
        unexpected outputs.

        The heuristics assume that the function prototype is on a single line
        and that the function ends with a ``}`` on a line by itself.

        Args:
           show: What to show.  Either a function name or a 2-tuple: either ``(start_regex,end_regex)`` or ``(start_line_number,end_line_number``).  Defaults to ``None`` which shows the whole file.
           demangle: Pass the assembly through ``c++filt`` first, so C++ symbols are more readable.  Defaults to ``True``.
        Returns:
           ``str`` : The preprocessed source code.
        
        """
        
        if language is None:
            language = infer_language(self.build_spec.source_file)

        compiled_source_base_name = self.extract_build_name(self.build_spec.source_file)
        preprocessed_suffix = self.compute_preprocessed_suffix(self.build_spec.source_file, language=language)
        source_file_to_search = self.compute_built_filename(f"{compiled_source_base_name}{preprocessed_suffix}")

        return filter_code(extract_code(source_file_to_search, self, show=show, language=language, **kwargs), filter)

    def compute_preprocessed_suffix(self, filename, language):
        if language is None:
            language = infer_language(filename)

        if language == "c++":
            return ".ii"
        elif language == "c":
            return ".i"
        else:
            raise InspectionError(f"Can't compute preprocessor file extension for file  '{filename}' in '{language}'.")

                
class InstrumentedExecutable(Preprocessed, Source, Assembly, CFG, DebugInfo, Executable):

    """A compiled source file.

    :obj:`Builder` objects create these when they compile code.  They can be passed to :func:`cfiddle.run` for execution.

    The compiled code is a dynamic library (i.e., a :code:`.so` file).  The path to the library is in :code:`lib`.

    """

    def __init__(self, *argc, **kwargs):
        super().__init__(*argc, **kwargs)



def extract_code(filename, executable, source=None, show=None, language=None, include_header=False):

    if source is None:
        source = contents_of(filename)

    lines = source.split("\n")

    if show is None:
        show = 0, len(lines)

    if language is None:
        language = infer_language(filename)

    if isinstance(show, str):
        show = construct_function_regex(executable, language, show)

    if len(show) == 2:
        if all([isinstance(x, str) for x in show]): 
            start_line, end_line = find_region_by_regex(lines, show)
        elif all([isinstance(x, int) for x in show]): 
            start_line, end_line = show
        else:
            raise InspectionError(f"{show} is not a valid specification of code to extract.")
    else:
        raise InspectionError(f"{show} is not a valid specification of code to extract.")

    src = "\n".join(lines[start_line:end_line])

    if include_header:
        src = build_header(filename, language,(start_line, end_line)) + src

    return src

def filter_code(contents, filt):

    if filt is None:
        return contents

    if not callable(filt):
        predicate = lambda x: re.search(filt, x) is not None
    else:
        predicate = filt
        
    return "\n".join(filter(predicate, contents.split("\n")))

def build_header(filename, language, show):
    comments_syntaxes = {"c++": ("// ", ""),
                         "go": ("// ", ""),
                         "gas": ("; ", ""),
                         "c": ("/* ", " */")}

    try:
        c = comments_syntaxes[language]
    except KeyError:
        raise InspectionError(f"Unknown comment syntax for language '{language}'.")

    return f"{c[0]}{filename}:{show[0]+1}-{show[1]} ({show[1] - show[0]} lines){c[1]}\n"


def construct_function_regex(executable, language, function):
    if language in [ "c++", "c"]:
        return (fr"[\s\*]{re.escape(function)}\s*\(", r"^\}")
    elif language == "gas":
        return executable.get_toolchain().get_asm_function_bookends(function)
    elif language == "gas":
        return (fr"^{re.escape(function)}:\s*", ".cfi_endproc")
    elif language == "go":
        return (fr"func\s+{re.escape(function)}", r"^\}")
    else:
        raise InspectionError(f"Don't know how to find functions in {language}")


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
    raise InspectionError(f"Couldn't find code for {show}")

def contents_of(f, flags="r"):
    with open(f, flags) as f:
        return f.read()
    
class InspectionError(CFiddleException):
    pass

