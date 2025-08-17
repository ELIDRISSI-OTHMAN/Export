"""
Runtime hook to fix import paths and DLL loading
"""
import os
import sys

# Fix DLL loading path
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    bundle_dir = sys._MEIPASS
    
    # Add bundle directory to PATH for DLL loading
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')
    
    # Add to Python path
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
        
    print(f"Runtime hook: Bundle directory = {bundle_dir}")
    print(f"Runtime hook: Updated PATH")