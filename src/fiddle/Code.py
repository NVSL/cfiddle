import hashlib
import os
from .util import read_file
from .config import get_config

def code(source, language=None):
    """Generate an anonymous source file.

    Write `source` to anonymous file and return the file's name.  This function
    is meant to be used an the first argument of :func:`build()`.

    Args:
      source: The source code.  Raw strings work best (e.g., `r\"\"\" // my code \"\"\"`).
      language:  Suffix to use for the filename.  Default to `cpp`.
    Returns:
      `str`: The file name.
    """
    
    if language is None:
        language = "cpp"
        
    file_name = _compute_anon_code_filename(source, language)
    _update_source(file_name, source)
    return file_name
    
def _compute_anon_code_filename(source, language):
    anon_source_directory = os.path.join(os.environ.get("FIDDLE_BUILD_ROOT", get_config("FIDDLE_BUILD_ROOT")), "anonymous_code")
    hash_value = hashlib.md5(source.encode('utf-8')).hexdigest()
    return os.path.join(anon_source_directory, f"{hash_value}.{language}")
    
def _update_source(source_file, source):
    if not os.path.exists(source_file) or read_file(source_file) != source:
        os.makedirs(os.path.dirname(source_file), exist_ok=True)
        with open(source_file, "w") as r:
            r.write(source)
