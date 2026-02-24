import sys
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QMouseEvent, QAction, QFont, QColor, QPalette, QIcon, QPixmap

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
        self.header_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header_label)

        # Splits List (simplified for now)
        self.splits_list = QListWidget()
        self.splits_list.setStyleSheet("background-color: transparent; border: none; color: white; font-family: 'Consolas', 'Courier New'; font-size: 14px;")
        self.splits_list.setIconSize(QSize(32, 32))
        layout.addWidget(self.splits_list)

        # Timer Display
        self.timer_label = QLabel("0.00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.timer_label.setStyleSheet("color: #00FF00; font-size: 48px; font-family: 'Consolas', 'Courier New'; font-weight: bold;")
        layout.addWidget(self.timer_label)

        # Footer
        footer_layout = QVBoxLayout()
        self.gold_label = QLabel("Best Segment: -")
        self.gold_label.setStyleSheet("color: #FFD700; font-size: 13px;") # Gold color
        footer_layout.addWidget(self.gold_label)
        
        self.sob_label = QLabel(f"Sum of Best: {self.format_time(self.run_state.get_sum_of_best())}")
        self.sob_label.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        footer_layout.addWidget(self.sob_label)
        
        hint_label = QLabel("Right-click for Settings")
        hint_label.setStyleSheet("color: #555555; font-size: 10px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer_layout.addWidget(hint_label)
        
        layout.addLayout(footer_layout)

        self.refresh_splits_ui()
        self.setFixedSize(400, 600)

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
            name = segment.name
            split_time_str = ""
            delta_str = ""
            
            if i < self.run_state.current_segment_index:
                # Past segments: show actual split time and delta vs PB
                split_time_str = self.format_time(segment.current_split_time)
                if segment.personal_best is not None and segment.current_split_time is not None:
                    delta = segment.current_split_time - segment.personal_best
                    delta_str = f"{delta:+.2f}"
            else:
                # Current/Future segments: show PB split time
                split_time_str = self.format_time(segment.personal_best)

            # Columnar layout using fixed-width characters (Consolas)
            # Layout: [Name (20)] [Delta (10)] [Split Time (10)]
            clean_text = f"{name[:20]:<20} {delta_str:<10} {split_time_str:<10}"
            item = QListWidgetItem(clean_text)

            if segment.icon_path and os.path.exists(segment.icon_path):
                pixmap = QPixmap(segment.icon_path)
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap))
            else:
                # If no icon or invalid, set a blank/transparent pixmap of the correct size
                # This reserves the space for the icon and ensures consistent text alignment.
                transparent_pixmap = QPixmap(self.splits_list.iconSize())
                transparent_pixmap.fill(Qt.GlobalColor.transparent)
                item.setIcon(QIcon(transparent_pixmap))


            # Delta coloring
            if delta_str:
                delta = float(delta_str)
                if delta < 0:
                    item.setForeground(QColor("#44FF44")) # Ahead (Green)
                else:
                    item.setForeground(QColor("#FF4444")) # Behind (Red)
            elif i == self.run_state.current_segment_index:
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
                # Auto-save on run completion
                save_run(self.run_state.run_data, self.current_file_path)
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
