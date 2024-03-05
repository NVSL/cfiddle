from contextlib import contextmanager
from functools import wraps

class CFiddleException(Exception):
    pass

class CFiddleInternalError(CFiddleException):
    def __init__(self, *args, original_exception=None):
        self.original_exception = original_exception
        super().__init__(*args)

class NoopExceptionHandler():
    """
    A default exception handler that does nothing.  
    """
    def handle_exception(self, e):
        """ 
        Handle an exception, :code:`e`.  This method should return :code:`True` if the exception was handled and :code:`False` otherwise,
        in which case the exception will be raised as usual.
        """
        return None
    
    @contextmanager
    def exception_handling(self):
        yield

    
class OutermostCallExceptionHandler():
    """
    Exception handler that only handles exception cleanly for the outermost call to a :func:`handle_cfiddle_execeptions`-wrapped function.
    """
    def is_outermost_call(self):
        from .config import get_config
        return get_config("_exception_handling_depth", 0) == 0

    # def handle_outermost_exception(self, e):
    #     raise NotImplementedError("Subclasses must implement this method.")
    
    # def handle_exception(self, e):
    #     from .config import get_config
    #     if self.is_outermost_call():
    #         return self.handle_outermost_exception(e)

    #     return None

    @contextmanager
    def exception_handling(self):
        from .config import get_config, cfiddle_config
        with cfiddle_config(_exception_handling_depth=get_config("_exception_handling_depth", 0) + 1, force=True):
            yield

class HideInternalErrorHandler(OutermostCallExceptionHandler):
    """
    Exception handler that hides internal errors.
    """
    def handle_exception(self, e):
        if not self.is_outermost_call():
            return None
        
        from .config import in_debug
        if isinstance(e, CFiddleException):
            return None
        else:
            if in_debug():
                return None
            return CFiddleInternalError(f"CFiddle encountered an internal error.  Call `enable_debug()` for full details and consider submitting a bug report:\n{str(e)}",
                                        original_exception=e)

def handle_cfiddle_exceptions(f):

    @wraps(f)
    def wrapped(*argc, **kwargs):
        from .config import get_config
        ExceptionHandler = get_config("ExceptionHandler_type")
        handler = ExceptionHandler()
        try:
            with handler.exception_handling():
                return f(*argc, **kwargs)
        except Exception as e:
            to_raise = handler.handle_exception(e)
            if to_raise is not None:
                raise to_raise
            raise
            
    return wrapped