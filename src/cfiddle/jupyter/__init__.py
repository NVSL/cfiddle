from tqdm.notebook import tqdm
from ..config import set_config, enable_interactive
from .source import FullyInstrumentedExecutable
from .util import compare
from .util import html_parameters


def configure_for_jupyter():
    """Set things up to run under Jupyter Notebook/lab

    This turns on Jupyter-aware progress bars and provide useful error messages
    rather than stack traces on error.  It also enable Jupyter-aware formatting
    for extract source code, assembly, etc.
    """
    set_config("Executable_type", FullyInstrumentedExecutable) 
    set_config("ProgressBar", tqdm)
    enable_interactive()

