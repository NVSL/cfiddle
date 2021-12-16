import re
import os
import subprocess
import pytest
import fiddle.source# import asm, preprocessed, source
from IPython.display import Image, IFrame, Code
import IPython

def html_parameters(parameter_set):
    return "<br/>".join([f"{p} = {v}" for p,v in parameter_set.items()])

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

def test_foo():
    import fiddle.MakeBuilder
    from fiddle.Builder import CompiledFunctionDelegator
    build = fiddle.MakeBuilder.MakeBuilder()
    build.register_analysis(fiddle.jupyter.source.source)
    build.register_analysis(fiddle.jupyter.source.asm)
#    build.register_analysis(fiddle.jupyter.cfg.cfg)
    build.register_analysis(fiddle.source.source, as_name="raw_source")
    build.register_analysis(fiddle.source.asm, as_name="raw_asm")
    build.register_analysis(CompiledFunctionDelegator, as_name="function")

    cse = build(code=r"""

    extern "C" int foo(register int a, register int b) {
       register int c = a * b;
       return a * b + c;
    }

    """, OPTIMIZE=["-O0", "-O1"]).function()

