#!/usr/bin/env python3
"""
Build script for creating installers for different platforms
"""

import os
import sys
import subprocess
import platform
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

def install_build_tools():
    """Install required build tools"""
    print("Installing build tools...")
    
    # Install PyInstaller
    if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
        return False
    
    # Install cx_Freeze as alternative
    if not run_command([sys.executable, "-m", "pip", "install", "cx_Freeze"]):
        print("Warning: cx_Freeze installation failed, continuing with PyInstaller only")
    
    # Platform-specific installers
    system = platform.system().lower()
    
    if system == "windows":
        # Install NSIS for Windows installer
        print("For Windows installer, please install NSIS from: https://nsis.sourceforge.io/")
        if not run_command([sys.executable, "-m", "pip", "install", "pynsist"]):
            print("Warning: pynsist installation failed")
    
    elif system == "darwin":  # macOS
        # Install create-dmg for macOS
        if not run_command([sys.executable, "-m", "pip", "install", "dmgbuild"]):
            print("Warning: dmgbuild installation failed")
    
    return True

def build_pyinstaller():
    """Build executable using PyInstaller"""
    print("\n=== Building with PyInstaller ===")
    
    # Create PyInstaller spec file
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('README.md', '.'),
        ('README_FR.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtOpenGLWidgets',
        'cv2',
        'numpy',
        'PIL',
        'openslide',
        'skimage',
        'scipy',
        'matplotlib',
        'tifffile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
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
    
    with open('tissue_fragment_stitching.spec', 'w') as f:
        f.write(spec_content)
    
    # Build with PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "tissue_fragment_stitching.spec"]
    return run_command(cmd)

def build_cx_freeze():
    """Build executable using cx_Freeze"""
    print("\n=== Building with cx_Freeze ===")
    
    setup_cx = '''
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': [
        'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtOpenGLWidgets',
        'cv2', 'numpy', 'PIL', 'openslide', 'skimage', 'scipy', 'matplotlib', 'tifffile'
    ],
    'excludes': ['tkinter'],
    'include_files': [
        ('src/', 'src/'),
        ('README.md', 'README.md'),
        ('README_FR.md', 'README_FR.md'),
    ],
}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        'main.py',
        base=base,
        target_name='TissueFragmentStitching',
        icon='icon.ico' if sys.platform == 'win32' else None
    )
]

setup(
    name='TissueFragmentStitching',
    version='1.0.0',
    description='Tissue Fragment Arrangement and Rigid Stitching UI',
    options={'build_exe': build_options},
    executables=executables
)
'''
    
    with open('setup_cx.py', 'w') as f:
        f.write(setup_cx)
    
    cmd = [sys.executable, "setup_cx.py", "build"]
    return run_command(cmd)

def create_windows_installer():
    """Create Windows installer using NSIS"""
    print("\n=== Creating Windows Installer ===")
    
    nsis_script = '''
!define APPNAME "Tissue Fragment Stitching"
!define COMPANYNAME "Scientific Imaging Lab"
!define DESCRIPTION "Professional desktop application for tissue fragment visualization and stitching"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://github.com/yourusername/tissue-fragment-stitching"
!define UPDATEURL "https://github.com/yourusername/tissue-fragment-stitching/releases"
!define ABOUTURL "https://github.com/yourusername/tissue-fragment-stitching"

!define INSTALLSIZE 500000  # Estimate in KB

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"

Name "${APPNAME}"
Icon "icon.ico"
outFile "TissueFragmentStitching-Setup.exe"

!include LogicLib.nsh

page components
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    
    # Copy files
    file /r "dist\\TissueFragmentStitching\\*"
    
    # Create uninstaller
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    # Start Menu
    createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\TissueFragmentStitching.exe" "" "$INSTDIR\\TissueFragmentStitching.exe"
    
    # Desktop shortcut
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\TissueFragmentStitching.exe" "" "$INSTDIR\\TissueFragmentStitching.exe"
    
    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$INSTDIR\\TissueFragmentStitching.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    # Remove Start Menu launcher
    delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${COMPANYNAME}"
    
    # Remove desktop shortcut
    delete "$DESKTOP\\${APPNAME}.lnk"
    
    # Remove files
    rmDir /r "$INSTDIR"
    
    # Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("NSIS script created. To build installer:")
    print("1. Install NSIS from https://nsis.sourceforge.io/")
    print("2. Run: makensis installer.nsi")

def create_macos_installer():
    """Create macOS installer"""
    print("\n=== Creating macOS Installer ===")
    
    # Create app bundle structure
    app_name = "TissueFragmentStitching.app"
    app_path = f"dist/{app_name}"
    
    os.makedirs(f"{app_path}/Contents/MacOS", exist_ok=True)
    os.makedirs(f"{app_path}/Contents/Resources", exist_ok=True)
    
    # Info.plist
    info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TissueFragmentStitching</string>
    <key>CFBundleIdentifier</key>
    <string>com.scientificimaging.tissuefragmentstitching</string>
    <key>CFBundleName</key>
    <string>Tissue Fragment Stitching</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
</dict>
</plist>'''
    
    with open(f"{app_path}/Contents/Info.plist", 'w') as f:
        f.write(info_plist)
    
    print(f"macOS app bundle created at {app_path}")
    print("To create DMG, install dmgbuild and run:")
    print(f"dmgbuild 'Tissue Fragment Stitching' TissueFragmentStitching.dmg -s dmg_settings.py")

def create_linux_package():
    """Create Linux package"""
    print("\n=== Creating Linux Package ===")
    
    # Create .desktop file
    desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=Tissue Fragment Stitching
Comment=Professional desktop application for tissue fragment visualization and stitching
Exec=/opt/TissueFragmentStitching/TissueFragmentStitching
Icon=/opt/TissueFragmentStitching/icon.png
Terminal=false
Categories=Science;Education;
'''
    
    with open('TissueFragmentStitching.desktop', 'w') as f:
        f.write(desktop_content)
    
    # Create install script
    install_script = '''#!/bin/bash
# Install script for Tissue Fragment Stitching

set -e

echo "Installing Tissue Fragment Stitching..."

# Create installation directory
sudo mkdir -p /opt/TissueFragmentStitching

# Copy files
sudo cp -r dist/TissueFragmentStitching/* /opt/TissueFragmentStitching/

# Make executable
sudo chmod +x /opt/TissueFragmentStitching/TissueFragmentStitching

# Install desktop file
sudo cp TissueFragmentStitching.desktop /usr/share/applications/

# Create symlink
sudo ln -sf /opt/TissueFragmentStitching/TissueFragmentStitching /usr/local/bin/tissue-fragment-stitching

echo "Installation complete!"
echo "You can now run the application from the applications menu or by typing 'tissue-fragment-stitching' in terminal."
'''
    
    with open('install.sh', 'w') as f:
        f.write(install_script)
    
    os.chmod('install.sh', 0o755)
    
    print("Linux installation files created:")
    print("- TissueFragmentStitching.desktop")
    print("- install.sh")

def main():
    """Main build function"""
    print("=== Tissue Fragment Stitching Installer Builder ===")
    
    # Install build tools
    if not install_build_tools():
        print("Failed to install build tools")
        return False
    
    # Create dist directory
    os.makedirs('dist', exist_ok=True)
    
    # Build executable
    success = False
    
    # Try PyInstaller first
    if build_pyinstaller():
        success = True
        print("✓ PyInstaller build successful")
    else:
        print("✗ PyInstaller build failed, trying cx_Freeze...")
        if build_cx_freeze():
            success = True
            print("✓ cx_Freeze build successful")
        else:
            print("✗ Both PyInstaller and cx_Freeze failed")
            return False
    
    if not success:
        return False
    
    # Create platform-specific installers
    system = platform.system().lower()
    
    if system == "windows":
        create_windows_installer()
    elif system == "darwin":
        create_macos_installer()
    else:  # Linux
        create_linux_package()
    
    print("\n=== Build Complete ===")
    print("Check the 'dist' directory for the built application")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)