#!/usr/bin/env python3
"""
Simple PyInstaller build script that works
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print("Success!")
    return True

def find_openslide_dlls():
    """Find OpenSlide DLL files"""
    dll_files = {}  # Use dict to avoid duplicates
    
    # Comprehensive search paths for OpenSlide DLLs
    search_paths = [
        Path(sys.prefix) / "Library" / "bin",
        Path(sys.prefix) / "Library" / "lib",
        Path(sys.prefix) / "DLLs",
        Path(sys.prefix) / "bin",
        Path(sys.prefix) / "Lib" / "site-packages" / "openslide_bin",
    ]
    
    # Add conda environment paths
    if 'CONDA_PREFIX' in os.environ:
        conda_prefix = Path(os.environ['CONDA_PREFIX'])
        search_paths.extend([
            conda_prefix / "Library" / "bin",
            conda_prefix / "Library" / "lib", 
            conda_prefix / "DLLs",
            conda_prefix / "bin",
            conda_prefix / "Lib" / "site-packages" / "openslide_bin",
        ])
    
    # Add virtual environment paths
    if 'VIRTUAL_ENV' in os.environ:
        venv_prefix = Path(os.environ['VIRTUAL_ENV'])
        search_paths.extend([
            venv_prefix / "Library" / "bin",
            venv_prefix / "Library" / "lib",
            venv_prefix / "DLLs", 
            venv_prefix / "bin",
            venv_prefix / "Lib" / "site-packages" / "openslide_bin",
        ])
    
    # Try to find openslide package location
    try:
        import openslide
        openslide_path = Path(openslide.__file__).parent
        search_paths.extend([
            openslide_path,
            openslide_path / "bin",
            openslide_path / "_bin",
            openslide_path.parent / "openslide_bin",
        ])
        print(f"Found openslide package at: {openslide_path}")
    except ImportError:
        print("OpenSlide package not found in Python path")
    
    print("Searching for OpenSlide DLLs...")
    
    for path in search_paths:
        if path.exists():
            print(f"  Checking: {path}")
            for dll in path.glob("*.dll"):
                dll_name = dll.name.lower()
                # More comprehensive DLL matching
                if (any(keyword in dll_name for keyword in [
                    'openslide', 'slide', 'jpeg', 'png', 'tiff', 'openjp2',
                    'zlib', 'cairo', 'glib', 'gobject', 'gdk', 'pixbuf',
                    'xml2', 'iconv', 'intl', 'ffi', 'pcre', 'harfbuzz'
                ]) or dll_name.startswith('lib')):
                    dll_files[dll.name] = str(dll)
                    print(f"    Found: {dll.name}")
    

def build_executable():
    """Build the executable using PyInstaller command line"""
    print("=== Building Executable ===")
    
    # Detect current environment
    current_env = None
    if 'CONDA_DEFAULT_ENV' in os.environ:
        current_env = os.environ['CONDA_DEFAULT_ENV']
        print(f"Current conda environment: {current_env}")
    elif 'VIRTUAL_ENV' in os.environ:
        current_env = os.path.basename(os.environ['VIRTUAL_ENV'])
        print(f"Current virtual environment: {current_env}")
    
    # Use the current Python executable (from active environment)
    python_exe = sys.executable
    python_dir = os.path.dirname(python_exe)
    
    print(f"Using Python executable: {python_exe}")
    print(f"Python directory: {python_dir}")
    
    # Clean previous builds
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")
    
    # Set up paths based on current environment
    python_dlls_dir = os.path.join(python_dir, 'DLLs')
    python_lib_dir = os.path.join(python_dir, 'Library', 'bin')
    site_packages = os.path.join(python_dir, 'Lib', 'site-packages')
    
    # Find OpenSlide DLLs
    openslide_dlls = find_openslide_dlls()
    
    # Find PyQt6 installation path
    try:
        import PyQt6
        pyqt6_path = os.path.dirname(PyQt6.__file__)
        print(f"PyQt6 path: {pyqt6_path}")
        
        # Verify PyQt6 is working
        from PyQt6.QtCore import QCoreApplication
        print("PyQt6 import test: SUCCESS")
    except ImportError:
        print(f"ERROR: PyQt6 not found in current environment! {e}")
        print(f"Current environment: {current_env}")
        print("Make sure PyQt6 is installed in your current environment:")
        print("  pip install PyQt6")
        return False
    
    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "TissueFragmentStitching",
        "--clean",
        
        # Add Python paths
        "--paths", python_dir,
        "--paths", python_dlls_dir,
        "--paths", python_lib_dir,
        "--paths", site_packages,
        "--paths", pyqt6_path,
        
        # Add data files
        "--add-data", "src;src",
        "--add-data", "README.md;.",
        
        # Collect all PyQt6 modules
        "--collect-all", "PyQt6",
        "--collect-all", "PyQt6.QtCore",
        "--collect-all", "PyQt6.QtGui", 
        "--collect-all", "PyQt6.QtWidgets",
        "--collect-all", "PyQt6.QtOpenGLWidgets",
        
        # Hidden imports
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui", 
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtOpenGLWidgets",
        "--hidden-import", "PyQt6.sip",
        "--hidden-import", "PyQt6.QtPrintSupport",
        "--hidden-import", "sip",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        "--hidden-import", "openslide",
        "--hidden-import", "openslide._convert",
        "--hidden-import", "openslide.lowlevel",
        "--hidden-import", "skimage",
        "--hidden-import", "skimage.feature",
        "--hidden-import", "skimage.transform",
        "--hidden-import", "scipy",
        "--hidden-import", "scipy.optimize",
        "--hidden-import", "matplotlib",
        "--hidden-import", "tifffile",
        "--hidden-import", "pkg_resources.py2_warn",
        
        # Exclude unnecessary modules
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib.tests",
        "--exclude-module", "numpy.tests",
        "--exclude-module", "scipy.tests",
        "--exclude-module", "torch",
        "--exclude-module", "tensorflow",
        "--exclude-module", "jupyter",
        "--exclude-module", "IPython",
        
        # Runtime options to help with DLL loading
        "--runtime-tmpdir", ".",
        
        "main.py"
    ]
    
    # Add OpenSlide DLLs
    if openslide_dlls:
        for dll in openslide_dlls:
            cmd.extend(["--add-binary", f"{dll};."])
    else:
        print("WARNING: No OpenSlide DLLs found - OpenSlide functionality may not work")
    
    # Run PyInstaller
    if not run_command(cmd):
        print("PyInstaller build failed")
        return False
    
    # Verify the build
    if sys.platform == "win32":
        exe_path = "dist/TissueFragmentStitching/TissueFragmentStitching.exe"
    else:
        exe_path = "dist/TissueFragmentStitching/TissueFragmentStitching"
        
    if os.path.exists(exe_path):
        print(f"Executable created: {exe_path}")
        
        # Verify OpenSlide DLLs are in the right place
        openslide_bin_dir = "dist/TissueFragmentStitching/openslide_bin"
        if os.path.exists(openslide_bin_dir):
            dll_count = len([f for f in os.listdir(openslide_bin_dir) if f.endswith('.dll')])
            print(f"OpenSlide DLLs copied: {dll_count}")
        else:
            print("WARNING: openslide_bin directory not found in dist")
            
        return True
    else:
        print("Executable not found after build")
        return False

def create_installer_script():
    """Create Inno Setup installer script"""
    inno_script = '''[Setup]
AppName=Tissue Fragment Stitching
AppVersion=1.0.0
AppPublisher=Scientific Imaging Lab
DefaultDirName={autopf}\\TissueFragmentStitching
DefaultGroupName=Tissue Fragment Stitching
OutputDir=installers
OutputBaseFilename=TissueFragmentStitching-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\\TissueFragmentStitching\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Tissue Fragment Stitching"; Filename: "{app}\\TissueFragmentStitching.exe"
Name: "{autodesktop}\\Tissue Fragment Stitching"; Filename: "{app}\\TissueFragmentStitching.exe"

[Run]
Filename: "{app}\\TissueFragmentStitching.exe"; Description: "Launch Tissue Fragment Stitching"; Flags: nowait postinstall skipifsilent
'''
    
    os.makedirs('installers', exist_ok=True)
    
    with open('installer.iss', 'w', encoding='utf-8') as f:
        f.write(inno_script)
    
    print("Installer script created: installer.iss")
    return True

def main():
    """Main build function"""
    print("=== Simple PyInstaller Build ===")
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer script
    create_installer_script()
    
    print("\n" + "="*50)
    print("BUILD COMPLETE!")
    print("="*50)
    print("\nFiles created:")
    print("   - dist/TissueFragmentStitching/ - Application files")
    print("   - installer.iss - Inno Setup script")
    print("\nNext steps:")
    print("   1. Test: dist/TissueFragmentStitching/TissueFragmentStitching.exe")
    print("   2. Install Inno Setup from: https://jrsoftware.org/isinfo.php")
    print("   3. Open installer.iss in Inno Setup")
    print("   4. Click Build > Compile")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)