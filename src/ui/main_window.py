import sys
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QMouseEvent, QAction, QFont, QColor, QPalette

from ..core.timer import Timer, TimerState
from ..core.state import RunState, Segment
from ..core.io import load_run, save_run

class TimesplitUI(QMainWindow):
    def __init__(self, run_state: RunState, file_path: str = None):
        super().__init__()
        self.run_state = run_state
        self.current_file_path = file_path or os.path.join("data", "example_run.json")
        self.timer = Timer()
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(33) # ~30fps update
        
        self.init_ui()
        self.set_transparency()
        self.old_pos = None

    def init_ui(self):
        self.setWindowTitle("Timesplit")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.header_label = QLabel(f"{self.run_state.run_data.game_name} - {self.run_state.run_data.category}")
        self.header_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.header_label)

        # Splits List (simplified for now)
        self.splits_list = QListWidget()
        self.splits_list.setStyleSheet("background-color: transparent; border: none; color: white;")
        layout.addWidget(self.splits_list)

        # Timer Display
        self.timer_label = QLabel("0.00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.timer_label.setStyleSheet("color: #00FF00; font-size: 36px; font-family: 'Courier New';")
        layout.addWidget(self.timer_label)

        # Footer
        footer_layout = QVBoxLayout()
        self.gold_label = QLabel("Best Segment: -")
        self.gold_label.setStyleSheet("color: #FFD700; font-size: 10px;") # Gold color
        footer_layout.addWidget(self.gold_label)
        
        self.sob_label = QLabel(f"Sum of Best: {self.format_time(self.run_state.get_sum_of_best())}")
        self.sob_label.setStyleSheet("color: #AAAAAA; font-size: 10px;")
        footer_layout.addWidget(self.sob_label)
        
        hint_label = QLabel("Right-click for Settings")
        hint_label.setStyleSheet("color: #555555; font-size: 8px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer_layout.addWidget(hint_label)
        
        layout.addLayout(footer_layout)

        self.refresh_splits_ui()
        self.setFixedSize(300, 450)

    def set_transparency(self):
        # Semi-transparent background with a subtle border
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 180);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
            QLabel {
                background: transparent;
                border: none;
            }
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
        """)

    def refresh_splits_ui(self):
        self.splits_list.clear()
        for i, segment in enumerate(self.run_state.run_data.segments):
            # Format: Segment Name | Delta | Split Time
            name = segment.name
            delta_str = ""
            split_time_str = self.format_time(segment.personal_best)
            
            if i < self.run_state.current_segment_index:
                # Segment finished, show actual split time and delta
                split_time_str = self.format_time(segment.current_split_time)
                if segment.personal_best is not None and segment.current_split_time is not None:
                    delta = segment.current_split_time - segment.personal_best
                    delta_str = f"{delta:+.2f}"
                    if delta < 0:
                        delta_str = f"<font color='#00FF00'>{delta_str}</font>" # Ahead
                    else:
                        delta_str = f"<font color='#FF0000'>{delta_str}</font>" # Behind

            display_text = f"{name:<20} {delta_str:>10} {split_time_str:>10}"
            item = QListWidgetItem()
            # We use a custom widget or HTML for coloring parts of the text
            # For simplicity in MVP, we'll just set the whole item color if not using HTML
            # Actually, QListWidgetItem doesn't support HTML easily. 
            # Let's use a simple format for now or just the name.
            
            clean_text = f"{name[:15]:<15} {split_time_str:>8}"
            item.setText(clean_text)

            if i == self.run_state.current_segment_index:
                item.setBackground(QColor(255, 255, 255, 30))
                item.setForeground(QColor("#FFFFFF"))
            elif i < self.run_state.current_segment_index:
                item.setForeground(QColor("#AAAAAA"))
            else:
                item.setForeground(QColor("#666666"))
            
            self.splits_list.addItem(item)
        
        # Update Footer
        current_seg = self.run_state.get_current_segment()
        if current_seg:
            self.gold_label.setText(f"Best Segment: {self.format_time(current_seg.gold)}")
        else:
            self.gold_label.setText("Best Segment: -")
            
        self.sob_label.setText(f"Sum of Best: {self.format_time(self.run_state.get_sum_of_best())}")

    def update_ui(self):
        current_time = self.timer.get_time()
        self.timer_label.setText(self.format_time(current_time))
        
        # Pace coloring
        if self.timer.state == TimerState.RUNNING:
            current_seg_index = self.run_state.current_segment_index
            if 0 <= current_seg_index < len(self.run_state.run_data.segments):
                segment = self.run_state.run_data.segments[current_seg_index]
                if segment.personal_best is not None:
                    if current_time > segment.personal_best:
                        self.timer_label.setStyleSheet("color: #FF4444; font-size: 36px; font-family: 'Courier New'; font-weight: bold;") # Behind
                    else:
                        self.timer_label.setStyleSheet("color: #44FF44; font-size: 36px; font-family: 'Courier New'; font-weight: bold;") # Ahead
                else:
                    self.timer_label.setStyleSheet("color: #FFFFFF; font-size: 36px; font-family: 'Courier New'; font-weight: bold;")
        elif self.timer.state == TimerState.FINISHED:
            last_seg = self.run_state.run_data.segments[-1]
            if last_seg.personal_best is not None and last_seg.current_split_time is not None:
                if last_seg.current_split_time < last_seg.personal_best:
                    self.timer_label.setStyleSheet("color: #00FFFF; font-size: 36px; font-family: 'Courier New'; font-weight: bold;") # Gold/PB Final
                else:
                    self.timer_label.setStyleSheet("color: #FF4444; font-size: 36px; font-family: 'Courier New'; font-weight: bold;")
        else:
            self.timer_label.setStyleSheet("color: #00FF00; font-size: 36px; font-family: 'Courier New'; font-weight: bold;")

    def format_time(self, seconds):
        if seconds is None: return "-"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds * 100) % 100)
        if minutes > 0:
            return f"{minutes}:{secs:02d}.{ms:02d}"
        return f"{secs}.{ms:02d}"

    # Actions
    def start_split(self):
        if self.timer.state == TimerState.STOPPED:
            self.timer.start()
            self.run_state.start()
            self.refresh_splits_ui()
        elif self.timer.state == TimerState.RUNNING:
            finished = self.run_state.split(self.timer.get_time())
            if finished:
                self.timer.finish()
            self.refresh_splits_ui()
        elif self.timer.state == TimerState.PAUSED:
            self.timer.start()

    def reset_timer(self):
        # Save before resetting if we had a run
        if self.run_state.current_segment_index > 0:
            save_run(self.run_state.run_data, self.current_file_path)
        
        self.timer.reset()
        self.run_state.reset()
        self.refresh_splits_ui()

    def closeEvent(self, event):
        save_run(self.run_state.run_data, self.current_file_path)
        event.accept()

    def undo_split(self):
        self.run_state.undo_split()
        self.refresh_splits_ui()

    def skip_split(self):
        self.run_state.skip_split()
        self.refresh_splits_ui()

    # Drag to move
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        context_menu.addAction(settings_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        context_menu.addAction(exit_action)
        context_menu.exec(event.globalPos())

    def open_settings(self):
        from .settings_window import SettingsWindow
        dialog = SettingsWindow(self)
        dialog.exec()
