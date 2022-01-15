import ctypes
from collections import namedtuple
from .PerformanceCounterSpec import PerformanceCounterSpec
from .perfcount_defs import *

class CacheCounter(PerformanceCounterSpec):
    def __init__(self, cache, op, result):
        #https://man7.org/linux/man-pages/man2/perf_event_open.2.html
        config = ((cache) |
                  (op << 8) |
                  (result << 16))
        super().__init__(PERF_TYPE_HW_CACHE, config)
        self.cache = cache
        self.op = op
        self.result = result



def install_perf_counters(perf_counters):
    libcfiddle = _load_libcfiddle()

    for pc in perf_counters:
        if isinstance(pc, CacheCounter):
            libcfiddle.add_cache_perf_counter(pc.cache, pc.op, pc.result)
        elif isinstance(pc, PerformanceCounterSpec):
            libcfiddle.add_perf_counter(pc.type, pc.config)
        else:
            raise ValueError("Expected instance of 'PerformanceCounterSpec' not {type(pc).__name__}.")

def are_perf_counters_available():
    return _load_libcfiddle().are_perf_counters_available()


def clear_perf_counters():
    _load_libcfiddle().clear_perf_counters()


def _load_libcfiddle():
    return  ctypes.CDLL("libcfiddle.so")

