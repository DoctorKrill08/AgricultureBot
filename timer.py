import time
class Timer():
    def __init__(self):
        self.start_time = time.perf_counter()
    def time_passed(self):
        return time.perf_counter() - self.start_time
    def reset(self):
        self.start_time = time.perf_counter()
class Stopwatch(Timer):
    def __init__(self):
        super().__init__()
        self.on = False
    def go(self):
        self.on = True
        self.start_time = time.perf_counter()
    def stop(self):
        self.on = False
    def time_passed(self):
        if (not self.on):
            return 0
        return super().time_passed()
    