from functools import wraps


class CFiddleException(Exception):
    pass

class NoopExceptionHandler():
    """
    A default exception handler that does nothing.  
    """
    def handle_exeception(self, e):
        """ 
        Handle an exception, :code:`e`.  This method should return :code:`True` if the exception was handled and :code:`False` otherwise,
        in which case the exception will be raised as usual.
        """
        return False

def handle_cfiddle_exceptions(f):
    from .config import in_debug, get_config


    @wraps(f)
    def wrapped(*argc, **kwargs):
        ExceptionHandler = get_config("ExceptionHandler_type")
        try:
            return f(*argc, **kwargs)
        except CFiddleException as e:
            if not ExceptionHandler().handle_exeception(e):
                raise
        except Exception as e:
            if in_debug():
                raise            
            to_raise = CFiddleException(f"CFiddle encountered an internal error.  Call `enable_debug()` for full details and consider submitting a bug report:\n{str(e)}")
            if not ExceptionHandler().handle_exeception(to_raise):
                raise to_raise
            
            
    return wrapped

        
