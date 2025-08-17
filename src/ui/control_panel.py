"""
Control panel for fragment manipulation
"""

from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                            QSlider, QCheckBox, QGridLayout, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core.fragment import Fragment

class ControlPanel(QWidget):
    """Control panel for fragment transformation and properties"""
    
    # Single fragment signals
    transform_requested = pyqtSignal(str, str, object)  # fragment_id, transform_type, value
    reset_transform_requested = pyqtSignal(str)  # fragment_id
    
    # Group signals
    group_rotate_requested = pyqtSignal(int)  # angle_degrees
    group_translate_requested = pyqtSignal(float, float)  # dx, dy
    
    def __init__(self):
        super().__init__()
        self.current_fragment: Optional[Fragment] = None
        self.group_size = 0
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        """Setup the control panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Single fragment tab
        self.fragment_tab = QWidget()
        self.setup_fragment_tab()
        self.tab_widget.addTab(self.fragment_tab, "Fragment")
        
        # Group selection tab
        self.group_tab = QWidget()
        self.setup_group_tab()
        self.tab_widget.addTab(self.group_tab, "Group")
        
        layout.addStretch()
        
    def setup_fragment_tab(self):
        """Setup single fragment controls"""
        layout = QVBoxLayout(self.fragment_tab)
        
        # Fragment info
        self.info_group = QGroupBox("Fragment Information")
        info_layout = QVBoxLayout(self.info_group)
        
        self.name_label = QLabel("No fragment selected")
        self.name_label.setStyleSheet("font-weight: bold; color: #4a90e2;")
        info_layout.addWidget(self.name_label)
        
        self.size_label = QLabel("Size: -")
        info_layout.addWidget(self.size_label)
        
        layout.addWidget(self.info_group)
        
        # Transform controls
        self.transform_group = QGroupBox("Transformations")
        transform_layout = QGridLayout(self.transform_group)
        
        # Rotation
        transform_layout.addWidget(QLabel("Rotation:"), 0, 0)
        
        rotation_layout = QHBoxLayout()
        self.rotate_ccw_btn = QPushButton("↺ 90°")
        self.rotate_ccw_btn.clicked.connect(lambda: self.request_transform('rotate_ccw'))
        rotation_layout.addWidget(self.rotate_ccw_btn)
        
        self.rotate_cw_btn = QPushButton("↻ 90°")
        self.rotate_cw_btn.clicked.connect(lambda: self.request_transform('rotate_cw'))
        rotation_layout.addWidget(self.rotate_cw_btn)
        
        transform_layout.addLayout(rotation_layout, 0, 1)
        
        # Flip
        transform_layout.addWidget(QLabel("Flip:"), 1, 0)
        
        flip_layout = QHBoxLayout()
        self.flip_h_btn = QPushButton("↔ Horizontal")
        self.flip_h_btn.clicked.connect(lambda: self.request_transform('flip_horizontal'))
        flip_layout.addWidget(self.flip_h_btn)
        
        self.flip_v_btn = QPushButton("↕ Vertical")
        self.flip_v_btn.clicked.connect(lambda: self.request_transform('flip_vertical'))
        flip_layout.addWidget(self.flip_v_btn)
        
        transform_layout.addLayout(flip_layout, 1, 1)
        
        layout.addWidget(self.transform_group)
        
        # Position controls
        self.position_group = QGroupBox("Position")
        position_layout = QGridLayout(self.position_group)
        
        # Movement buttons
        self.up_btn = QPushButton("↑")
        self.up_btn.clicked.connect(lambda: self.request_transform('translate', (0, -10)))
        position_layout.addWidget(self.up_btn, 0, 1)
        
        self.left_btn = QPushButton("←")
        self.left_btn.clicked.connect(lambda: self.request_transform('translate', (-10, 0)))
        position_layout.addWidget(self.left_btn, 1, 0)
        
        self.right_btn = QPushButton("→")
        self.right_btn.clicked.connect(lambda: self.request_transform('translate', (10, 0)))
        position_layout.addWidget(self.right_btn, 1, 2)
        
        self.down_btn = QPushButton("↓")
        self.down_btn.clicked.connect(lambda: self.request_transform('translate', (0, 10)))
        position_layout.addWidget(self.down_btn, 2, 1)
        
        layout.addWidget(self.position_group)
        
    def setup_group_tab(self):
        """Setup group controls"""
        layout = QVBoxLayout(self.group_tab)
        
        # Group info
        self.group_info_group = QGroupBox("Group Information")
        group_info_layout = QVBoxLayout(self.group_info_group)
        
        self.group_name_label = QLabel("No group selected")
        self.group_name_label.setStyleSheet("font-weight: bold; color: #4a90e2;")
        group_info_layout.addWidget(self.group_name_label)
        
        layout.addWidget(self.group_info_group)
        
        # Group rotation
        self.group_rotation_group = QGroupBox("Group Rotation")
        rotation_layout = QHBoxLayout(self.group_rotation_group)
        
        self.group_rotate_ccw_btn = QPushButton("↺ 90° CCW")
        self.group_rotate_ccw_btn.setMinimumHeight(60)
        self.group_rotate_ccw_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #4a90e2;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a9bd4;
            }
            QPushButton:pressed {
                background-color: #3a80d2;
            }
        """)
        self.group_rotate_ccw_btn.clicked.connect(lambda: self.group_rotate_requested.emit(-90))
        rotation_layout.addWidget(self.group_rotate_ccw_btn)
        
        self.group_rotate_cw_btn = QPushButton("↻ 90° CW")
        self.group_rotate_cw_btn.setMinimumHeight(60)
        self.group_rotate_cw_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #4a90e2;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a9bd4;
            }
            QPushButton:pressed {
                background-color: #3a80d2;
            }
        """)
        self.group_rotate_cw_btn.clicked.connect(lambda: self.group_rotate_requested.emit(90))
        rotation_layout.addWidget(self.group_rotate_cw_btn)
        
        layout.addWidget(self.group_rotation_group)
        
        # Group movement
        self.group_movement_group = QGroupBox("Group Movement")
        movement_layout = QGridLayout(self.group_movement_group)
        
        # Movement buttons
        self.group_up_btn = QPushButton("↑")
        self.group_up_btn.setMinimumSize(50, 50)
        self.group_up_btn.clicked.connect(lambda: self.group_translate_requested.emit(0, -10))
        movement_layout.addWidget(self.group_up_btn, 0, 1)
        
        self.group_left_btn = QPushButton("←")
        self.group_left_btn.setMinimumSize(50, 50)
        self.group_left_btn.clicked.connect(lambda: self.group_translate_requested.emit(-10, 0))
        movement_layout.addWidget(self.group_left_btn, 1, 0)
        
        self.group_right_btn = QPushButton("→")
        self.group_right_btn.setMinimumSize(50, 50)
        self.group_right_btn.clicked.connect(lambda: self.group_translate_requested.emit(10, 0))
        movement_layout.addWidget(self.group_right_btn, 1, 2)
        
        self.group_down_btn = QPushButton("↓")
        self.group_down_btn.setMinimumSize(50, 50)
        self.group_down_btn.clicked.connect(lambda: self.group_translate_requested.emit(0, 10))
        movement_layout.addWidget(self.group_down_btn, 2, 1)
        
        layout.addWidget(self.group_movement_group)
        
    def set_selected_fragment(self, fragment: Optional[Fragment]):
        """Set single fragment selection"""
        self.current_fragment = fragment
        self.group_size = 0
        self.update_display()
        
    def set_group_selection(self, group_size: int):
        """Set group selection"""
        self.current_fragment = None
        self.group_size = group_size
        self.update_display()
        
    def update_display(self):
        """Update the display based on current selection"""
        print(f"ControlPanel: Updating display - fragment={self.current_fragment is not None}, group_size={self.group_size}")
        
        if self.group_size > 1:
            # Group selection mode
            print("ControlPanel: Switching to group mode")
            self.tab_widget.setCurrentWidget(self.group_tab)
            self.group_tab.setEnabled(True)
            self.fragment_tab.setEnabled(False)
            
            # Update group info
            self.group_name_label.setText(f"Group Selection ({self.group_size} fragments)")
            
            # Enable group controls
            self.group_rotation_group.setEnabled(True)
            self.group_movement_group.setEnabled(True)
            self.group_rotate_ccw_btn.setEnabled(True)
            self.group_rotate_cw_btn.setEnabled(True)
            
        elif self.current_fragment:
            # Single fragment mode
            print("ControlPanel: Switching to fragment mode")
            self.tab_widget.setCurrentWidget(self.fragment_tab)
            self.fragment_tab.setEnabled(True)
            self.group_tab.setEnabled(False)
            
            # Update fragment info
            fragment = self.current_fragment
            self.name_label.setText(fragment.name or f"Fragment {fragment.id[:8]}")
            self.size_label.setText(f"Size: {fragment.original_size[0]} × {fragment.original_size[1]}")
            
            # Enable fragment controls
            self.transform_group.setEnabled(True)
            self.position_group.setEnabled(True)
            
        else:
            # No selection
            print("ControlPanel: No selection mode")
            self.tab_widget.setCurrentWidget(self.fragment_tab)
            self.fragment_tab.setEnabled(True)
            self.group_tab.setEnabled(False)
            
            self.name_label.setText("No fragment selected")
            self.size_label.setText("Size: -")
            
            self.transform_group.setEnabled(False)
            self.position_group.setEnabled(False)
            
    def request_transform(self, transform_type: str, value=None):
        """Request single fragment transformation"""
        if self.current_fragment:
            self.transform_requested.emit(self.current_fragment.id, transform_type, value)