import re
import os
import subprocess
import pytest
import fiddle.source# import asm, preprocessed, source
from IPython.display import Image, IFrame, Code

def asm(build_result, *argc, **kwargs):
    asm_source = fiddle.source.asm(*argc, **kwangs)
    return Code(asm_source, language="gas")

def preprocessed(build_result, *argc, **kwargs):
    language = kwargs.get("language")
    if language is None:
        language = fiddle.source.infer_language(build_result.source_file)

    preprocessed_source = fiddle.source.preprocessed_source(*argc, **kwargs)
    return Code(preprocessed_source, language=language)

def source(build_result, *argc, **kwargs):
    language = kwargs.get("language")
    if language is None:
        language = fiddle.source.infer_language(build_result.source_file)

    raw_source = fiddle.source.source(build_result, *argc, **kwargs)
    return Code(raw_source, language=language)

