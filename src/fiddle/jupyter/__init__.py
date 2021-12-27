from fiddle.config import set_config
from .source import FullyInstrumentedExecutable
from .util import compare

def running_under_jupyter():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    return 'ipykernel' in sys.modules


def configure_for_jupyter():
    set_config("Executable_type", FullyInstrumentedExecutable) 

