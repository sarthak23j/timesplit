from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QSlider, QFileDialog, QListWidget, QListWidgetItem, QWidget, QCheckBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import os
from ..core.io import load_run, save_run
from ..core.state import RunData, Segment

class SegmentEditorWidget(QWidget):
    def __init__(self, segment: Segment = None, parent=None):
        super().__init__(parent)
        self.segment = segment if segment else Segment("New Segment")
        self.setMinimumHeight(40)
        self.init_ui()
        self.setStyleSheet("background-color: transparent;") # Make widget transparent

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.icon_button = QPushButton()
        self.icon_button.setFixedSize(30, 30) # Slightly larger button
        self.icon_button.setIconSize(QSize(24, 24))
        self.icon_button.clicked.connect(self.browse_icon)
        layout.addWidget(self.icon_button)

        self.name_edit = QLineEdit(self.segment.name)
        self.name_edit.setPlaceholderText("Segment Name")
        layout.addWidget(self.name_edit, 1) # Give name edit stretch factor

        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(24, 24)
        layout.addWidget(self.checkbox)

        self.load_icon()

        # Connect name edit to update segment object
        self.name_edit.textChanged.connect(self._update_segment_name)

    def _update_segment_name(self, name):
        self.segment.name = name

    def browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Image Files (*.png *.jpg *.bmp *.gif)")
        if file_path:
            self.segment.icon_path = file_path
            self.load_icon()

    def load_icon(self):
        if self.segment.icon_path and os.path.exists(self.segment.icon_path):
            pixmap = QPixmap(self.segment.icon_path)
            if not pixmap.isNull():
                self.icon_button.setIcon(QIcon(pixmap))
            else:
                self.icon_button.setIcon(QIcon()) # Clear icon
        else:
            self.icon_button.setIcon(QIcon()) # Clear icon


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timesplit Settings")
        self.setModal(True)
        self.parent_ui = parent
        self.current_run_data = None
        
        self.apply_styles()
        
        if parent and hasattr(parent, 'run_state'):
            self.current_run_data = parent.run_state.run_data
        self.init_ui()
        if self.current_run_data:
            self.load_data_into_ui(self.current_run_data)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #bbbbbb;
                font-size: 13px;
                font-weight: bold;
                margin-top: 5px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton#saveButton {
                background-color: #0078d4;
                font-weight: bold;
            }
            QPushButton#saveButton:hover {
                background-color: #0086f0;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #ffffff;
                font-size: 13px;
                padding: 0px; /* Remove padding here */
            }
            QListWidget::item {
                background-color: transparent; /* Make item background transparent */
                margin: 0px; /* Remove margin here */
                padding: 0px; /* Remove padding here */
            }
            QListWidget::item:selected {
                background-color: #0078d4; /* This should now be visible through transparent widget */
                border-radius: 4px; /* Apply border radius to selected item background */
            }
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 8px;
                background: #2d2d2d;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
                /* image: url(assets/checkmark_white.png); -- Add a white checkmark image here later */
            }
            QCheckBox::indicator:hover {
                border: 1px solid #00aaff;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Transparency Slider
        layout.addWidget(QLabel("OVERLAY TRANSPARENCY"))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(50, 255)
        self.alpha_slider.setValue(180)
        self.alpha_slider.valueChanged.connect(self.update_transparency)
        layout.addWidget(self.alpha_slider)

        layout.addSpacing(10)

        # File Selection
        layout.addWidget(QLabel("SPLIT FILE"))
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("No file loaded...")
        if self.parent_ui and hasattr(self.parent_ui, 'current_file_path'):
            self.file_path_edit.setText(self.parent_ui.current_file_path)
        file_layout.addWidget(self.file_path_edit)
        
        load_btn = QPushButton("Browse")
        load_btn.clicked.connect(self.load_file)
        file_layout.addWidget(load_btn)
        layout.addLayout(file_layout)

        layout.addSpacing(10)

        # Split Editor
        layout.addWidget(QLabel("RUN DETAILS"))
        self.game_name_edit = QLineEdit()
        self.game_name_edit.setPlaceholderText("Game Name (e.g., Super Mario 64)")
        layout.addWidget(self.game_name_edit)

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Category (e.g., Any%)")
        layout.addWidget(self.category_edit)

        layout.addSpacing(5)
        layout.addWidget(QLabel("SEGMENTS"))
        self.segments_list = QListWidget()
        self.segments_list.setSelectionMode(QListWidget.SelectionMode.NoSelection) # Disable default selection highlighting
        layout.addWidget(self.segments_list, 1) # Give it a stretch factor of 1

        seg_ctrl_layout = QHBoxLayout()
        add_seg_btn = QPushButton("+ Add")
        add_seg_btn.clicked.connect(self.add_segment)
        seg_ctrl_layout.addWidget(add_seg_btn)

        remove_seg_btn = QPushButton("- Remove")
        remove_seg_btn.clicked.connect(self.remove_segment)
        seg_ctrl_layout.addWidget(remove_seg_btn)
        layout.addLayout(seg_ctrl_layout)

        layout.addSpacing(20)

        # Save/Apply
        self.save_btn = QPushButton("SAVE & APPLY")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        self.setMinimumWidth(450)
        self.setMinimumHeight(775)

    def load_data_into_ui(self, run_data: RunData):
        self.game_name_edit.setText(run_data.game_name)
        self.category_edit.setText(run_data.category)
        self.segments_list.clear()
        for seg in run_data.segments:
            item = QListWidgetItem(self.segments_list)
            editor = SegmentEditorWidget(seg)
            item.setSizeHint(editor.sizeHint())
            self.segments_list.addItem(item)
            self.segments_list.setItemWidget(item, editor)

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
            self.current_run_data = load_run(file_path)
            self.load_data_into_ui(self.current_run_data)

    def add_segment(self):
        item = QListWidgetItem(self.segments_list)
        editor = SegmentEditorWidget()
        item.setSizeHint(editor.sizeHint())
        self.segments_list.addItem(item)
        self.segments_list.setItemWidget(item, editor)

    def remove_segment(self):
        items_to_remove = []
        for i in range(self.segments_list.count()):
            item = self.segments_list.item(i)
            editor = self.segments_list.itemWidget(item)
            if editor and editor.checkbox.isChecked():
                items_to_remove.append(item)
        
        for item in reversed(items_to_remove): # Remove from end to avoid index issues
            row = self.segments_list.row(item)
            self.segments_list.takeItem(row)

    def save_settings(self):
        segments = []
        for i in range(self.segments_list.count()):
            item = self.segments_list.item(i)
            editor = self.segments_list.itemWidget(item)
            segments.append(editor.segment) # SegmentEditorWidget manages its own Segment object
        
        new_run_data = RunData(
            game_name=self.game_name_edit.text() or "New Game",
            category=self.category_edit.text() or "Any%",
            segments=segments,
            attempts=self.current_run_data.attempts if self.current_run_data else 0
        )

        file_path = self.file_path_edit.text()
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Split File", "data", "JSON Files (*.json)")
        
        if file_path:
            save_run(new_run_data, file_path)
            if self.parent_ui:
                from ..core.state import RunState
                self.parent_ui.run_state = RunState(new_run_data)
                self.parent_ui.current_file_path = file_path
                self.parent_ui.header_label.setText(f"{new_run_data.game_name} - {new_run_data.category}")
                self.parent_ui.reset_timer()
            self.accept()
