import hashlib
import os
from .util import read_file
from .config import get_config
from .paths import cfiddle_lib_path, cfiddle_include_path
from .Exceptions import CFiddleException

def code(source, language=None, raw=False):
    """Generate an anonymous source file and return the path to it.

    Write ``source`` to anonymous file and return the file's name.  This function
    is meant to be used an the first argument of :func:`build()`.

    Args:
      source:    The source code.  Raw strings work best (e.g., `r\"\"\" // my code \"\"\"`).
      language:  Suffix to use for the filename.  Default to `cpp`.
      raw:       Don't add language-specific boilerplate. (Default: :code:`False`)
    Returns:
      ``str``: The file name.
    """
    
    if language is None:
        language = "cpp"

    if not raw:
        if language not in language_decorators:
            raise UnknownLanguageSuffix(f"Unknown suffix '{language}'.  Options are: {list(language_decorators.keys())}")
        source = language_decorators[language](source)

    
    
    file_name = _compute_anon_code_filename(source, language)
    _update_source(file_name, source)
    return file_name

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

def _compute_anon_code_filename(source, language):
    anon_source_directory = os.path.join(os.environ.get("CFIDDLE_BUILD_ROOT", get_config("CFIDDLE_BUILD_ROOT")), "anonymous_code")
    hash_value = hashlib.md5(source.encode('utf-8')).hexdigest()
    return os.path.join(anon_source_directory, f"{hash_value}.{language}")
    
def _update_source(source_file, source):
    if not os.path.exists(source_file) or read_file(source_file) != source:
        os.makedirs(os.path.dirname(source_file), exist_ok=True)
        with open(source_file, "w") as r:
            r.write(source)

            
language_decorators ={"go": _decorate_go_code,
                      "c": _decorate_c_code,
                      "cpp":_decorate_cpp_code,
                      "cxx":_decorate_cpp_code,
                      "c++":_decorate_cpp_code}

class UnknownLanguageSuffix(CFiddleException):
    pass
