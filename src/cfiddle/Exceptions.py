from functools import wraps

class CFiddleException(Exception):
    pass


def handle_cfiddle_exceptions(f):
    from .config import in_debug

    @wraps(f)
    def wrapped(*argc, **kwargs):
        try:
            return f(*argc, **kwargs)
        except CFiddleException as e:
            raise
        except Exception as e:
            if in_debug():
                raise
            raise CFiddleException(f"CFiddle encountered an internal error.  Call `enable_debug()` for full details and consider submitting a bug report:\n{str(e)}") from None
            
    return wrapped

        
