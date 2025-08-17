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
    """Find ALL DLL files from virtual environment"""
    dll_files = []
    
    # Get all DLL locations in virtual environment
    search_paths = [
        Path(sys.executable).parent / "Library" / "bin",
        Path(sys.executable).parent / "Library" / "lib", 
        Path(sys.executable).parent / "DLLs",
        Path(sys.executable).parent / "bin",
        Path(sys.executable).parent / "Lib" / "site-packages",
    ]
    
    print("Searching for ALL DLLs in virtual environment...")
    
    for path in search_paths:
        if path.exists():
            print(f"  Checking: {path}")
            # Find ALL DLLs recursively
            for dll in path.rglob("*.dll"):
                dll_files.append(str(dll))
                print(f"    Found: {dll.name}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_dlls = []
    for dll in dll_files:
        if dll not in seen:
            seen.add(dll)
            unique_dlls.append(dll)
    
    print(f"Total unique DLLs found: {len(unique_dlls)}")
    return unique_dlls
    

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
    print(f"Total DLLs to include: {len(openslide_dlls)}")
    
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
        print("Make sure PyQt6 is installed in your current environment:")
        print("  pip install PyQt6")
        return False
    
    # Create spec file to avoid command line length issues
    spec_content = create_spec_file(python_dir, pyqt6_path, all_dlls)
    
    with open('app.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created app.spec file")
    
    # Build using spec file
    cmd = [python_exe, "-m", "PyInstaller", "--clean", "app.spec"]
    
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
        return True
    else:
        print("Executable not found after build")
        return False

def create_spec_file(python_dir, pyqt6_path, all_dlls):
    """Create PyInstaller spec file"""
    
    # Create binaries list
    binaries_list = []
    for dll in all_dlls:
        binaries_list.append(f"(r'{dll}', '.')")
    
    binaries_str = ",\n        ".join(binaries_list)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'{python_dir}', r'{pyqt6_path}'],
    binaries=[
        {binaries_str}
    ],
    datas=[
        ('src', 'src'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtOpenGLWidgets',
        'PyQt6.sip',
        'PyQt6.QtPrintSupport',
        'sip',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'openslide',
        'openslide._convert',
        'openslide.lowlevel',
        'skimage',
        'skimage.feature',
        'skimage.transform',
        'scipy',
        'scipy.optimize',
        'matplotlib',
        'tifffile',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
        'torch',
        'tensorflow',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TissueFragmentStitching',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TissueFragmentStitching',
)
'''
    return spec_content

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