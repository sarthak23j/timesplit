import time
from enum import Enum, auto

class TimerState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()

class Timer:
    def __init__(self):
        self.start_time = 0
        self.elapsed_offset = 0
        self.state = TimerState.STOPPED

    def start(self):
        if self.state == TimerState.STOPPED:
            self.start_time = time.perf_counter()
            self.elapsed_offset = 0
            self.state = TimerState.RUNNING
        elif self.state == TimerState.PAUSED:
            self.start_time = time.perf_counter()
            self.state = TimerState.RUNNING

    def pause(self):
        if self.state == TimerState.RUNNING:
            self.elapsed_offset += time.perf_counter() - self.start_time
            self.state = TimerState.PAUSED

    def reset(self):
        self.start_time = 0
        self.elapsed_offset = 0
        self.state = TimerState.STOPPED

    def finish(self):
        if self.state == TimerState.RUNNING:
            self.elapsed_offset += time.perf_counter() - self.start_time
        self.state = TimerState.FINISHED

    def get_time(self):
        if self.state == TimerState.RUNNING:
            return self.elapsed_offset + (time.perf_counter() - self.start_time)
        return self.elapsed_offset

    def is_running(self):
        return self.state == TimerState.RUNNING
