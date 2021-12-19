import hashlib
import os
from .util import read_file

def code(source,language=None):
    if language is None:
        language = "cpp"
        
    file_name = _compute_anon_code_filename(source, language)
    _update_source(file_name, source)
    return file_name
    
def _compute_anon_code_filename(source, language):
    anon_source_directory = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/anonymous_code")
    hash_value = hashlib.md5(source.encode('utf-8')).hexdigest()
    return os.path.join(anon_source_directory, f"{hash_value}.{language}")
    
def _update_source(source_file, source):
    if not os.path.exists(source_file) or read_file(source_file) != source:
        os.makedirs(os.path.dirname(source_file), exist_ok=True)
        with open(source_file, "w") as r:
            r.write(source)
            
                
