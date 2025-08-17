#!/usr/bin/env python3
"""
Build installer for Tissue Fragment Stitching application
Creates executable with all required DLLs from virtual environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print(f"Success: {result.stdout}")
        return True
    except Exception as e:
        print(f"Command failed: {e}")
        return False

def find_all_dlls(search_dir):
    """Find all DLL files in the given directory"""
    dlls = []
    search_path = Path(search_dir)
    
    print(f"Searching for DLLs in: {search_path}")
    
    for dll_file in search_path.rglob("*.dll"):
        dlls.append(str(dll_file))
        print(f"Found DLL: {dll_file}")
    
    print(f"Total DLLs found: {len(dlls)}")
    return dlls

def create_spec_file(python_dir, all_dlls):
    """Create PyInstaller spec file with all DLLs"""
    
    # Format DLL binaries for spec file
    dll_binaries = []
    for dll in all_dlls:
        dll_path = Path(dll)
        dll_binaries.append(f"(r'{dll}', '.')")
    
    dll_binaries_str = ",\n    ".join(dll_binaries)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[r'{os.getcwd()}'],
    binaries=[
        {dll_binaries_str}
    ],
    datas=[
        ('src', 'src'),
        ('README.md', '.'),
        ('requirements.txt', '.')
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtOpenGLWidgets',
        'openslide',
        'openslide._convert',
        'openslide.lowlevel',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'tifffile',
        'scipy',
        'scipy.optimize',
        'scipy.ndimage',
        'skimage',
        'skimage.feature',
        'skimage.measure',
        'skimage.transform',
        'matplotlib',
        'matplotlib.pyplot'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
        'PIL.tests'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    
    with open('TissueFragmentStitching.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created TissueFragmentStitching.spec")
    return True

def install_build_tools():
    """Install required build tools"""
    print("Installing build tools...")
    
    tools = ['pyinstaller', 'auto-py-to-exe']
    
    for tool in tools:
        if not run_command([sys.executable, '-m', 'pip', 'install', tool]):
            print(f"Failed to install {tool}")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Get Python environment directory
    python_dir = Path(sys.executable).parent
    print(f"Python directory: {python_dir}")
    
    # Find all DLLs in the virtual environment
    all_dlls = find_all_dlls(python_dir)
    print(f"Found {len(all_dlls)} DLL files to include")
    
    # Create spec file
    if not create_spec_file(python_dir, all_dlls):
        return False
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Build using spec file
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'TissueFragmentStitching.spec']
    
    if not run_command(cmd):
        print("PyInstaller build failed")
        return False
    
    print("Executable built successfully!")
    return True

def create_installer_scripts():
    """Create platform-specific installer scripts"""
    print("Creating installer scripts...")
    
    # Windows NSIS installer script
    nsis_script = '''
; NSIS installer script for Tissue Fragment Stitching
!define APPNAME "Tissue Fragment Stitching"
!define COMPANYNAME "Scientific Imaging Lab"
!define DESCRIPTION "Professional tissue fragment visualization and stitching"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!include "MUI2.nsh"

Name "${APPNAME}"
OutFile "TissueFragmentStitching-Setup.exe"
InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\\TissueFragmentStitching\\*"
    
    CreateDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\TissueFragmentStitching.exe"
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\TissueFragmentStitching.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\\${COMPANYNAME}"
    
    RMDir /r "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("Created installer.nsi")
    return True

def main():
    """Main build process"""
    print("=== Tissue Fragment Stitching Build Script ===")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Not running in a virtual environment")
        print("Current Python:", sys.executable)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    current_env = os.environ.get('CONDA_DEFAULT_ENV') or os.environ.get('VIRTUAL_ENV', 'Unknown')
    print(f"Current environment: {current_env}")
    
    # Install build tools
    if not install_build_tools():
        print("Failed to install build tools")
        return False
    
    # Build executable
    if not build_executable():
        print("Failed to build executable")
        return False
    
    # Create installer scripts
    if not create_installer_scripts():
        print("Failed to create installer scripts")
        return False
    
    print("\n=== Build Complete! ===")
    print("Executable: dist/TissueFragmentStitching/TissueFragmentStitching.exe")
    print("Installer script: installer.nsi")
    print("\nTo create Windows installer:")
    print("1. Install NSIS from https://nsis.sourceforge.io/")
    print("2. Right-click installer.nsi and select 'Compile NSIS Script'")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    print("Build completed successfully!")