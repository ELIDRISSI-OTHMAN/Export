#!/usr/bin/env python3
"""
Tissue Fragment Arrangement and Rigid Stitching UI
Main application entry point
"""

import sys
import os

# Fix OpenSlide DLL loading issues at runtime
def fix_openslide_path():
    """Fix OpenSlide DLL path issues"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        app_dir = os.path.dirname(sys.executable)
        
        # Add potential OpenSlide DLL locations to PATH
        dll_paths = [
            os.path.join(app_dir, 'openslide_bin'),
            os.path.join(app_dir, '_internal', 'openslide_bin'),
            os.path.join(app_dir, '_internal'),
            app_dir
        ]
        
        for dll_path in dll_paths:
            if os.path.exists(dll_path):
                if dll_path not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = dll_path + os.pathsep + os.environ.get('PATH', '')

# Apply the fix before importing anything else
fix_openslide_path()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    #QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    #QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Tissue Fragment Stitching Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Scientific Imaging Lab")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme
    from src.ui.theme import apply_dark_theme
    apply_dark_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()