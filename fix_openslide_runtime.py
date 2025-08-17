#!/usr/bin/env python3
"""
Runtime fix for OpenSlide DLL loading issues
This script should be run if the built executable still has OpenSlide issues
"""

import os
import sys
import shutil
from pathlib import Path

def fix_openslide_runtime():
    """Fix OpenSlide DLL loading at runtime"""
    
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent / "dist" / "TissueFragmentStitching"
    
    print(f"Application directory: {app_dir}")
    
    # Check if openslide_bin directory exists
    openslide_bin_dir = app_dir / "openslide_bin"
    internal_dir = app_dir / "_internal"
    
    if not openslide_bin_dir.exists() and internal_dir.exists():
        # Look for DLLs in _internal directory
        internal_openslide = internal_dir / "openslide_bin"
        if internal_openslide.exists():
            print(f"Found OpenSlide DLLs in: {internal_openslide}")
            
            # Add to PATH so OpenSlide can find them
            dll_path = str(internal_openslide)
            if dll_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = dll_path + os.pathsep + os.environ.get('PATH', '')
                print(f"Added to PATH: {dll_path}")
        
        # Also add _internal to PATH
        internal_path = str(internal_dir)
        if internal_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = internal_path + os.pathsep + os.environ.get('PATH', '')
            print(f"Added to PATH: {internal_path}")
    
    # Try to preload critical DLLs
    critical_dlls = [
        'libopenslide-1.dll',
        'libopenslide-0.dll', 
        'openslide.dll'
    ]
    
    for dll_name in critical_dlls:
        # Search for the DLL
        dll_locations = [
            app_dir / dll_name,
            openslide_bin_dir / dll_name,
            internal_dir / dll_name,
            internal_dir / "openslide_bin" / dll_name
        ]
        
        for dll_path in dll_locations:
            if dll_path.exists():
                try:
                    import ctypes
                    ctypes.CDLL(str(dll_path))
                    print(f"Successfully preloaded: {dll_name}")
                    break
                except Exception as e:
                    print(f"Failed to preload {dll_name}: {e}")
                    continue

if __name__ == "__main__":
    fix_openslide_runtime()