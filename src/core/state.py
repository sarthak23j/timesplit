from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Segment:
    name: str
    personal_best: Optional[float] = None  # Cumulative time at the end of segment in PB run
    gold: Optional[float] = None           # Best ever duration for THIS segment
    current_duration: Optional[float] = None
    current_split_time: Optional[float] = None

@dataclass
class RunData:
    game_name: str
    category: str
    segments: List[Segment]
    attempts: int = 0
    offset: float = 0.0

class RunState:
    def __init__(self, run_data: RunData):
        self.run_data = run_data
        self.current_segment_index = -1
        self.start_time = 0
        self.segment_start_times = [] # Real time when segment started
        self.history = [] # To support Undo

    def start(self):
        self.current_segment_index = 0
        self.run_data.attempts += 1
        for s in self.run_data.segments:
            s.current_duration = None
            s.current_split_time = None

    def split(self, total_elapsed: float):
        if self.current_segment_index < 0 or self.current_segment_index >= len(self.run_data.segments):
            return False

        segment = self.run_data.segments[self.current_segment_index]
        segment.current_split_time = total_elapsed
        
        # Calculate duration
        prev_split_time = 0
        if self.current_segment_index > 0:
            prev_split_time = self.run_data.segments[self.current_segment_index - 1].current_split_time
        
        segment.current_duration = total_elapsed - prev_split_time

        # Update Gold if it's better
        if segment.gold is None or segment.current_duration < segment.gold:
            segment.gold = segment.current_duration

        self.current_segment_index += 1
        
        if self.current_segment_index == len(self.run_data.segments):
            # Check for New PB
            last_segment = self.run_data.segments[-1]
            if last_segment.personal_best is None or last_segment.current_split_time < last_segment.personal_best:
                # Update all PBs
                for s in self.run_data.segments:
                    s.personal_best = s.current_split_time
            return True # Finished
        return False

    def undo_split(self):
        if self.current_segment_index > 0:
            self.current_segment_index -= 1
            segment = self.run_data.segments[self.current_segment_index]
            segment.current_duration = None
            segment.current_split_time = None

    def skip_split(self):
        if self.current_segment_index >= 0 and self.current_segment_index < len(self.run_data.segments):
            self.run_data.segments[self.current_segment_index].current_split_time = None
            self.run_data.segments[self.current_segment_index].current_duration = None
            self.current_segment_index += 1

    def reset(self):
        self.current_segment_index = -1

    def get_current_segment(self) -> Optional[Segment]:
        if 0 <= self.current_segment_index < len(self.run_data.segments):
            return self.run_data.segments[self.current_segment_index]
        return None

    def get_sum_of_best(self) -> float:
        sob = 0.0
        for s in self.run_data.segments:
            if s.gold is not None:
                sob += s.gold
        return sob
