#!/usr/bin/env python3
"""
Simple build script that works
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
    print(f"Success: {result.stdout}")
    return True

def install_build_dependencies():
    """Install required build tools"""
    print("Installing build dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0",
    ]
    
    for dep in dependencies:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"Failed to install {dep}")
            return False
    
    return True

def create_simple_spec():
    """Create a simple spec file that works"""
    spec_content = '''# Simple spec file
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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
        'cv2',
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.lib.format',
        'PIL',
        'PIL.Image',
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add OpenSlide binaries
def find_openslide_dlls():
    binaries = []
    try:
        import openslide
        openslide_path = Path(openslide.__file__).parent
        
        # Search paths
        search_paths = [
            Path(sys.prefix) / "Library" / "bin",
            Path(sys.prefix) / "DLLs",
            openslide_path / "bin",
            openslide_path / "_bin",
        ]
        
        for path in search_paths:
            if path.exists():
                for dll in path.glob("*.dll"):
                    if any(x in dll.name.lower() for x in ['openslide', 'slide', 'jpeg', 'png', 'tiff', 'openjp2']):
                        binaries.append((str(dll), "."))
                        print(f"Found DLL: {dll.name}")
        
    except Exception as e:
        print(f"OpenSlide DLL search failed: {e}")
    
    return binaries

openslide_binaries = find_openslide_dlls()
a.binaries += openslide_binaries

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
    
    with open('simple.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return True

def build_executable():
    """Build the executable"""
    print("=== Building Executable ===")
    
    # Clean previous builds
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")
    
    # Create spec file
    if not create_simple_spec():
        return False
    
    # Build with PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "simple.spec"]
    if not run_command(cmd):
        print("PyInstaller build failed")
        return False
    
    # Verify the build
    exe_path = "dist/TissueFragmentStitching/TissueFragmentStitching.exe"
    if os.path.exists(exe_path):
        print(f"Executable created: {exe_path}")
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
    print("=== Simple Build Script ===")
    
    # Install dependencies
    if not install_build_dependencies():
        return False
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer script
    create_installer_script()
    
    print("\n" + "="*50)
    print("BUILD COMPLETE!")
    print("="*50)
    print("\nFiles created:")
    print("   • dist/TissueFragmentStitching/ - Application files")
    print("   • installer.iss - Inno Setup script")
    print("\nNext steps:")
    print("   1. Test: dist/TissueFragmentStitching/TissueFragmentStitching.exe")
    print("   2. Install Inno Setup from: https://jrsoftware.org/isinfo.php")
    print("   3. Open installer.iss in Inno Setup")
    print("   4. Click Build > Compile")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)