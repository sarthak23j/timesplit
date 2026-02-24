from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QSlider, QFileDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
import os
from ..core.io import load_run, save_run
from ..core.state import RunData, Segment

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timesplit Settings")
        self.setModal(True)
        self.parent_ui = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Transparency Slider
        layout.addWidget(QLabel("Transparency:"))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(50, 255)
        self.alpha_slider.setValue(180)
        self.alpha_slider.valueChanged.connect(self.update_transparency)
        layout.addWidget(self.alpha_slider)

        # File Selection
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        load_btn = QPushButton("Load Split")
        load_btn.clicked.connect(self.load_file)
        file_layout.addWidget(load_btn)
        layout.addLayout(file_layout)

        # Split Editor
        layout.addWidget(QLabel("Splits Editor:"))
        self.game_name_edit = QLineEdit()
        self.game_name_edit.setPlaceholderText("Game Name")
        layout.addWidget(self.game_name_edit)

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Category")
        layout.addWidget(self.category_edit)

        self.segments_list = QListWidget()
        layout.addWidget(self.segments_list)

        seg_ctrl_layout = QHBoxLayout()
        add_seg_btn = QPushButton("Add Segment")
        add_seg_btn.clicked.connect(self.add_segment)
        seg_ctrl_layout.addWidget(add_seg_btn)

        remove_seg_btn = QPushButton("Remove Selected")
        remove_seg_btn.clicked.connect(self.remove_segment)
        seg_ctrl_layout.addWidget(remove_seg_btn)
        layout.addLayout(seg_ctrl_layout)

        # Save/Apply
        save_btn = QPushButton("Save & Apply")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setMinimumWidth(400)

    def update_transparency(self, value):
        if self.parent_ui:
            self.parent_ui.setStyleSheet(f"""
                QWidget {{
                    background-color: rgba(20, 20, 20, {value});
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 30);
                }}
                QLabel {{ background: transparent; border: none; }}
                QListWidget {{ background: transparent; border: none; outline: none; }}
            """)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Split File", "data", "JSON Files (*.json)")
        if file_path:
            self.file_path_edit.setText(file_path)
            run_data = load_run(file_path)
            self.game_name_edit.setText(run_data.game_name)
            self.category_edit.setText(run_data.category)
            self.segments_list.clear()
            for seg in run_data.segments:
                item = QListWidgetItem(seg.name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.segments_list.addItem(item)

    def add_segment(self):
        item = QListWidgetItem("New Segment")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.segments_list.addItem(item)

    def remove_segment(self):
        for item in self.segments_list.selectedItems():
            self.segments_list.takeItem(self.segments_list.row(item))

    def save_settings(self):
        # Create new RunData from UI
        segments = []
        for i in range(self.segments_list.count()):
            name = self.segments_list.item(i).text()
            segments.append(Segment(name))
        
        new_run_data = RunData(
            game_name=self.game_name_edit.text() or "New Game",
            category=self.category_edit.text() or "Any%",
            segments=segments
        )

        # Ask where to save if no file loaded
        file_path = self.file_path_edit.text()
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Split File", "data", "JSON Files (*.json)")
        
        if file_path:
            save_run(new_run_data, file_path)
            if self.parent_ui:
                from ..core.state import RunState
                self.parent_ui.run_state = RunState(new_run_data)
                self.parent_ui.header_label.setText(f"{new_run_data.game_name} - {new_run_data.category}")
                self.parent_ui.reset_timer()
            self.accept()
