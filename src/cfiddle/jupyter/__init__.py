from tqdm.notebook import tqdm
from ..config import set_config
from .source import InstrumentedExecutable
from .util import compare
from .util import html_parameters


def configure_for_jupyter():
    """Set things up to run under Jupyter Notebook/lab

    This turns on Jupyter-aware progress bars and provide useful error messages
    rather than stack traces on error.  It also enable Jupyter-aware formatting
    for extract source code, assembly, etc.
    """
    set_config("Executable_type", InstrumentedExecutable) 
    set_config("ProgressBar", tqdm)


