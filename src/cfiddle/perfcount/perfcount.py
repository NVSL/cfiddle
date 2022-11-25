import ctypes
from ..Exceptions import CFiddleException

def install_perf_counters(perf_counters):
    libcfiddle = _load_libcfiddle()

    for pc in perf_counters:
        if isinstance(pc, str):
            libcfiddle.add_perf_counter(ctypes.c_char_p(pc.encode()))
        else:
            raise UnknownPerformanceCounter(f"Expected instance of 'str' not {type(pc).__name__}.")

        if not libcfiddle.check_valid_perfcounters():
            raise UnknownPerformanceCounter(f"Failed to add performance counter '{pc}'.")
        
def are_perf_counters_available():
    return bool(_load_libcfiddle().are_perf_counters_available())


def clear_perf_counters():
    _load_libcfiddle().clear_perf_counters()


def _load_libcfiddle():
    return  ctypes.CDLL("libcfiddle.so")


class UnknownPerformanceCounter(CFiddleException):
    pass
