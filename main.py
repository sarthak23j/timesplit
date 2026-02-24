import sys
import os
import keyboard
from PyQt6.QtWidgets import QApplication
from src.core.state import RunState, RunData, Segment
from src.ui.main_window import TimesplitUI

def create_example_run():
    segments = [
        Segment("Segment 1"),
        Segment("Segment 2"),
        Segment("Segment 3"),
        Segment("Final Segment")
    ]
    return RunData("Example Game", "Any%", segments)

def main():
    app = QApplication(sys.argv)
    
    # Try to load example data
    json_path = os.path.join("data", "example_run.json")
    if os.path.exists(json_path):
        from src.core.io import load_run
        run_data = load_run(json_path)
    else:
        run_data = create_example_run()
    
    run_state = RunState(run_data)
    
    window = TimesplitUI(run_state)
    window.show()

    print("Timesplit started!")
    print("Hotkeys:")
    print("  NumPad 1: Start / Split")
    print("  NumPad 3: Reset")
    print("  NumPad 8: Undo")
    print("  NumPad 2: Skip")
    print("  NumPad 5: Pause / Resume")

    # Register Hotkeys (using 'keyboard' library)
    # keyboard library needs to run in separate thread or hook into app
    # but for simple global hotkeys, we can use hooks
    
    keyboard.on_press_key("num 1", lambda _: window.start_split())
    keyboard.on_press_key("num 3", lambda _: window.reset_timer())
    keyboard.on_press_key("num 8", lambda _: window.undo_split())
    keyboard.on_press_key("num 2", lambda _: window.skip_split())
    keyboard.on_press_key("num 5", lambda _: window.timer.pause())

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
