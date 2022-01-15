
# this is by itself in this file to avoid circular dependence.

class PerformanceCounterSpec:
    def __init__(self, type, config):
        self.type = type
        self.config = config

