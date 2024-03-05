from tqdm.notebook import tqdm
from ..config import set_config
from .source import InstrumentedExecutable
from .util import compare
from .util import html_parameters
from .ExceptionHandler import PrettyExceptionHandler, CFiddleUserException


def configure_for_jupyter():
    """Set things up to run under Jupyter Notebook/lab

    This turns on Jupyter-aware progress bars.  It also enables
    Jupyter-aware formatting for extracting source code, assembly, etc.

    """
    set_config("Executable_type", InstrumentedExecutable) 
#    set_config("ProgressBar", tqdm)
    set_config("ExceptionHandler_type", PrettyExceptionHandler)


