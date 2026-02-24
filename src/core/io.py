import json
import os
from .state import RunData, Segment

def save_run(run_data: RunData, filepath: str):
    data = {
        "game_name": run_data.game_name,
        "category": run_data.category,
        "attempts": run_data.attempts,
        "offset": run_data.offset,
        "segments": [
            {
                "name": s.name,
                "personal_best": s.personal_best,
                "gold": s.gold
            } for s in run_data.segments
        ]
    }
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_run(filepath: str) -> RunData:
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    segments = [
        Segment(
            name=s["name"],
            personal_best=s.get("personal_best"),
            gold=s.get("gold")
        ) for s in data["segments"]
    ]
    
    return RunData(
        game_name=data["game_name"],
        category=data["category"],
        attempts=data.get("attempts", 0),
        offset=data.get("offset", 0.0),
        segments=segments
    )
