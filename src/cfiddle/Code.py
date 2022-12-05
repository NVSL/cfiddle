import hashlib
import os
import re

from .util import read_file
from .config import get_config
from .paths import cfiddle_lib_path, cfiddle_include_path
from .Exceptions import CFiddleException

def code(source, file_name=None, language=None, raw=False):
    """Generate an anonymous (by default) source file and return the path to it.

    Write ``source`` to anonymous file and return the file's name.  This function
    is meant to be used an the first argument of :func:`build()`.

    You can choose the location of the file, by speciying
    :code:`file_name`.  If the contents of the file has changed since
    :func:`code()` last wrote it, it will raise
    :obj:`SourceCodeModified` to prevent deleting your edits.

    Use :code:`language` to specify the language you are writing it.
    
    For some languages, :func:`code()` adds some boilerplate to make
    compilation work.  You can prevent this with :code:`raw=True`.
    
    Args:
      source:    The source code.  Raw strings work best (e.g., `r\"\"\" // my code \"\"\"`).
      file_name: Where to put the source code.  This file will be overwritten.
      language:  Suffix to use for the filename.  Default to `cpp`.
      raw:       Don't add language-specific boilerplate. (Default: :code:`False`)
    Returns:
      ``str``: The file name.

    """
    
    if language is None:
        language = "cpp"

    if not raw:
        source = _decorate_source(source, language)

    if file_name is None:
        file_name = _compute_anon_code_filename(source, language)

    if _change_detected(file_name):
        raise SourceCodeModified(f"The contents of {file_name} have changed since cfiddle wrote them last.  Aborting to prevent loss of work.")

    if not raw:
        source = _add_checksum(source, language)
    
    _update_source(file_name, source)
    return file_name


def _change_detected(file_name):
    if not os.path.exists(file_name): # doesn't exist
        return False 
    source = read_file(file_name)
    if not "Cfiddle-signature" in source: # we didn't write this file
        return True

    lines = source.split("\n")
    if "Cfiddle-signature" not in lines[-1]: # something was appended.
        return True

    m = re.search("Cfiddle-signature=([0-9a-f]+)", lines[-1])
    if not m:  # the line is mangled, so it must have been edited
        return True
    else:
        old_sig = m.group(1)
        new_sig = _hash("\n".join(lines[:-1]))
        if old_sig != new_sig: # something has changed.
            return True

    return False

def _hash(source):
    m = hashlib.md5()
    m.update(source.encode())
    return m.hexdigest()

def _add_checksum(source, language):
    if language not in append_comment:
        raise UnknownLanguageSuffix(f"Unknown suffix '{language}'.  Options are: {list(language_decorators.keys())}")
    signature = _hash(source)
    return append_comment[language](source, f"Cfiddle-signature={signature}")


def _decorate_source(source, language):
    if language not in language_decorators:
        raise UnknownLanguageSuffix(f"Unknown suffix '{language}'.  Options are: {list(language_decorators.keys())}")
    return language_decorators[language](source)

def _decorate_go_code(source):
    return f""" 
package main

// #cgo LDFLAGS: -L{cfiddle_lib_path()}  -lcfiddle
// #cgo CFLAGS: -g -Wall -I{cfiddle_include_path()}
// #include "cfiddle.h"
import "C"

{source}

func main() {{}}
"""

def _decorate_c_code(source):
    return source

def _decorate_cpp_code(source):
    return source

def _append_c_comment(source, comment):
    return source + f"\n/* {comment} */"

def _append_cpp_comment(source, comment):
        return source + f"\n// {comment}"

def _compute_anon_code_filename(source, language):
    anon_source_directory = os.path.join(os.environ.get("CFIDDLE_BUILD_ROOT", get_config("CFIDDLE_BUILD_ROOT")), "anonymous_code")
    hash_value = hashlib.md5(source.encode('utf-8')).hexdigest()
    return os.path.join(anon_source_directory, f"{hash_value}.{language}")
    
def _update_source(source_file, source):
    if not os.path.exists(source_file) or read_file(source_file) != source:
        directory = os.path.dirname(source_file)
        if directory == "":
            directory = "."
        else:
            os.makedirs(directory, exist_ok=True)
        with open(source_file, "w") as r:
            r.write(source)

            
language_decorators ={"go": _decorate_go_code,
                      "c": _decorate_c_code,
                      "cpp":_decorate_cpp_code,
                      "cxx":_decorate_cpp_code,
                      "c++":_decorate_cpp_code}

append_comment  ={"go": _append_cpp_comment,
                  "c": _append_c_comment,
                  "cpp":_append_cpp_comment,
                  "cxx":_append_cpp_comment,
                  "c++":_append_cpp_comment}

class UnknownLanguageSuffix(CFiddleException):
    pass
class SourceCodeModified(CFiddleException):
    pass
