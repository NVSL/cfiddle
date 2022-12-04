import os
try:
    import IPython
except ImportError:
    pass
from IPython.display import Image,SVG

import cfiddle.source
import cfiddle.DebugInfo
from cfiddle import Executable
from cfiddle.CFG.cfg import CFG

class Source(cfiddle.source.Source):

    def source(self, *argc, **kwargs):
        language = kwargs.get("language", cfiddle.source.infer_language(self.build_spec.source_file))
        source = super().source(*argc, **kwargs)
        return Code_hacked(source, language=language)

    def raw_source(self, *argc, **kwargs):
        return super().source(*argc, **kwargs)
    
class Assembly(cfiddle.source.Assembly):
    def asm(self, *argc, **kwargs):
        return Code_hacked(super().asm(*argc, **kwargs), language="gas")

    def raw_asm(self,*argc, **kwargs):
        return super().asm(*argc, **kwargs)

class Preprocessed(cfiddle.source.Preprocessed):
    
    def preprocessed(self, *argc, **kwargs):
        language = kwargs.get("language", cfiddle.source.infer_language(self.build_spec.source_file))
        preprocessed_source = super().preprocessed(*argc, **kwargs)
        return Code_hacked(preprocessed_source, language=language)

    def raw_preprocessed(self, *argc, **kwargs):
        return super().preprocessed(*argc, **kwargs)

class DebugInfo(cfiddle.DebugInfo.DebugInfo):
    def debug_info(self, *argc, **kwargs):
        return super().debug_info(*argc, **kwargs)
    
class CFG(CFG):
    def cfg(self, function, *argc, **kwargs):
        filename = os.path.join(self.build_dir, function) + ".svg"
        
        t = super().cfg(function, output=filename, *argc, **kwargs, jupyter=True)

        return SVG(t)
    
    
class InstrumentedExecutable(Preprocessed, Source, Assembly, CFG, DebugInfo, Executable):
    def __init__(self, *argc, **kwargs):
        super().__init__(*argc, **kwargs)


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
