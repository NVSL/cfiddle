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
            if in_debug():
                raise
            else:
                raise CFiddleException(e) from None
             
    return wrapped

        
