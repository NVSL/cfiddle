import re
import os
import subprocess
import pytest
import fiddle.source# import asm, preprocessed, source
from IPython.display import Image, IFrame, Code


import IPython

# This is a hack for jupyter lab
def Code_hacked(code, language):
    # https://github.com/ipython/ipython/issues/11747#issuecomment-528694702
    def _jupyterlab_repr_html_(self):
        from pygments import highlight
        from pygments.formatters import HtmlFormatter

        fmt = HtmlFormatter()
        style = "<style>{}\n{}</style>".format(
            fmt.get_style_defs(".output_html"), fmt.get_style_defs(".jp-RenderedHTML")
        )
        return style + highlight(self.data, self._get_lexer(), fmt)

    # Replace _repr_html_ with our own version that adds the 'jp-RenderedHTML' class
    # in addition to 'output_html'.
    IPython.display.Code._repr_html_ = _jupyterlab_repr_html_
    return IPython.display.Code(data=code, language=language)


def asm(build_result, *argc, **kwargs):
    asm_source = fiddle.source.asm(build_result, *argc, **kwargs)
    return Code_hacked(asm_source, language="gas")

def preprocessed(build_result, *argc, **kwargs):
    language = kwargs.get("language")
    if language is None:
        language = fiddle.source.infer_language(build_result.source_file)

    preprocessed_source = fiddle.source.preprocessed_source(build_result, *argc, **kwargs)
    return Code_hacked(preprocessed_source, language=language)

def source(build_result, *argc, **kwargs):
    language = kwargs.get("language")
    if language is None:
        language = fiddle.source.infer_language(build_result.source_file)

    raw_source = fiddle.source.source(build_result, *argc, **kwargs)
    return Code_hacked(raw_source, language=language)

