from functools import wraps
from click import secho

class CFiddleException(Exception):
    pass

def handle_cfiddle_exceptions(f):
    from .config import in_debug, get_config

    @wraps(f)
    def wrapped(*argc, **kwargs):

        try:
            return f(*argc, **kwargs)
        except CFiddleException as e:
            if in_debug():
                raise
            else:
                if get_config("DONT_RAISE"):
                    secho(f"CFiddle encountered an error (call `enable_debug()` for full details):\n{str(e)}", fg="red")
                    return None
                else:
                    raise e from None
                
        except Exception as e:
            if get_config("DONT_RAISE"):
                secho(f"CFiddle experienced an internal error (call `enable_debug()` for full details):\n{str(e)}", fg="red")
                return None
            else:
                raise e
            
    return wrapped

        
