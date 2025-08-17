#!/usr/bin/env python3
"""
Build script for creating simple click-to-install executables
Creates .exe for Windows, .dmg for macOS, .deb for Linux
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

def install_build_dependencies():
    """Install all required build tools"""
    print("Installing build dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0",
        "auto-py-to-exe",  # GUI for PyInstaller
        "pywin32; sys_platform=='win32'",  # Windows-specific
    ]
    
    for dep in dependencies:
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"Failed to install {dep}")
            return False
    
    # Install OpenSlide separately on Windows
    if platform.system().lower() == "windows":
        print("Installing OpenSlide for Windows...")
        if not run_command([sys.executable, "-m", "pip", "install", "openslide-python", "--force-reinstall"]):
            print("Warning: OpenSlide installation may have issues")
    
    return True

def create_pyinstaller_spec():
    """Create PyInstaller spec file for consistent builds"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Find OpenSlide DLLs on Windows
openslide_binaries = []
if sys.platform == 'win32':
    try:
        import openslide
        openslide_path = Path(openslide.__file__).parent
        dll_path = openslide_path / 'bin'
        if dll_path.exists():
            for dll_file in dll_path.glob('*.dll'):
                openslide_binaries.append((str(dll_file), 'openslide_bin'))
        print(f"Found OpenSlide DLLs: {len(openslide_binaries)}")
    except ImportError:
        print("OpenSlide not found - some features may not work")

# Find OpenCV DLLs
opencv_binaries = []
try:
    import cv2
    cv2_path = Path(cv2.__file__).parent
    for dll_file in cv2_path.glob('*.dll'):
        opencv_binaries.append((str(dll_file), '.'))
except ImportError:
    pass

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=openslide_binaries + opencv_binaries,
    datas=[
        ('src', 'src'),
        ('README.md', '.'),
        ('README_FR.md', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.QtOpenGLWidgets',
        'cv2',
        'numpy',
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
        'ctypes',
        'ctypes.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
        'PIL.ImageTk',  # Tkinter dependency
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
    
    with open('app.spec', 'w') as f:
        f.write(spec_content)
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n=== Building Executable ===")
    
    # Check OpenSlide installation
    try:
        import openslide
        print(f"✓ OpenSlide found at: {openslide.__file__}")
    except ImportError:
        print("⚠️  OpenSlide not found - some features may not work")
    
    # Create spec file
    if not create_pyinstaller_spec():
        return False
    
    # Build with PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--log-level=INFO", "app.spec"]
    if not run_command(cmd):
        print("PyInstaller build failed")
        return False
    
    print("✓ Executable built successfully")
    
    # Verify OpenSlide DLLs are included
    if platform.system().lower() == "windows":
        dist_path = Path("dist/TissueFragmentStitching")
        openslide_bin = dist_path / "openslide_bin"
        if openslide_bin.exists():
            dll_count = len(list(openslide_bin.glob("*.dll")))
            print(f"✓ OpenSlide DLLs included: {dll_count}")
        else:
            print("⚠️  OpenSlide DLLs may be missing")
    
    return True

def create_windows_installer():
    """Create Windows .exe installer using Inno Setup script"""
    print("\n=== Creating Windows Installer ===")
    
    # Create Inno Setup script
    inno_script = '''[Setup]
AppName=Tissue Fragment Stitching
AppVersion=1.0.0
AppPublisher=Scientific Imaging Lab
AppPublisherURL=https://github.com/yourusername/tissue-fragment-stitching
AppSupportURL=https://github.com/yourusername/tissue-fragment-stitching/issues
AppUpdatesURL=https://github.com/yourusername/tissue-fragment-stitching/releases
DefaultDirName={autopf}\\TissueFragmentStitching
DefaultGroupName=Tissue Fragment Stitching
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installers
OutputBaseFilename=TissueFragmentStitching-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\TissueFragmentStitching\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Tissue Fragment Stitching"; Filename: "{app}\\TissueFragmentStitching.exe"
Name: "{group}\\{cm:UninstallProgram,Tissue Fragment Stitching}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\Tissue Fragment Stitching"; Filename: "{app}\\TissueFragmentStitching.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\TissueFragmentStitching.exe"; Description: "{cm:LaunchProgram,Tissue Fragment Stitching}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
'''
    
    # Create installers directory
    os.makedirs('installers', exist_ok=True)
    
    with open('installer.iss', 'w') as f:
        f.write(inno_script)
    
    print("Inno Setup script created: installer.iss")
    print("\nTo create Windows installer:")
    print("1. Download and install Inno Setup from: https://jrsoftware.org/isinfo.php")
    print("2. Open installer.iss in Inno Setup")
    print("3. Click Build > Compile")
    print("4. The installer will be created in the 'installers' folder")
    
    return True

def create_macos_installer():
    """Create macOS .dmg installer"""
    print("\n=== Creating macOS Installer ===")
    
    app_name = "TissueFragmentStitching.app"
    
    # Create app bundle structure
    app_path = f"dist/{app_name}"
    contents_path = f"{app_path}/Contents"
    macos_path = f"{contents_path}/MacOS"
    resources_path = f"{contents_path}/Resources"
    
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # Copy executable
    if os.path.exists("dist/TissueFragmentStitching"):
        shutil.copytree("dist/TissueFragmentStitching", macos_path, dirs_exist_ok=True)
    
    # Create Info.plist
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
    <key>CFBundleDisplayName</key>
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
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>'''
    
    with open(f"{contents_path}/Info.plist", 'w') as f:
        f.write(info_plist)
    
    # Create DMG creation script
    dmg_script = f'''#!/bin/bash
# Create DMG installer for macOS

APP_NAME="Tissue Fragment Stitching"
DMG_NAME="TissueFragmentStitching-Installer"
APP_PATH="dist/{app_name}"

# Create temporary DMG directory
mkdir -p dmg_temp
cp -R "$APP_PATH" dmg_temp/

# Create Applications symlink
ln -s /Applications dmg_temp/Applications

# Create DMG
hdiutil create -volname "$APP_NAME" -srcfolder dmg_temp -ov -format UDZO "installers/$DMG_NAME.dmg"

# Cleanup
rm -rf dmg_temp

echo "DMG created: installers/$DMG_NAME.dmg"
'''
    
    with open('create_dmg.sh', 'w') as f:
        f.write(dmg_script)
    
    os.chmod('create_dmg.sh', 0o755)
    
    print(f"macOS app bundle created: {app_path}")
    print("To create DMG installer:")
    print("1. Run: ./create_dmg.sh")
    print("2. The .dmg file will be in the 'installers' folder")
    
    return True

def create_linux_installer():
    """Create Linux .deb package"""
    print("\n=== Creating Linux Installer ===")
    
    # Create debian package structure
    pkg_name = "tissue-fragment-stitching"
    pkg_version = "1.0.0"
    pkg_dir = f"debian_package/{pkg_name}_{pkg_version}"
    
    # Create directory structure
    debian_dir = f"{pkg_dir}/DEBIAN"
    opt_dir = f"{pkg_dir}/opt/TissueFragmentStitching"
    apps_dir = f"{pkg_dir}/usr/share/applications"
    bin_dir = f"{pkg_dir}/usr/local/bin"
    
    os.makedirs(debian_dir, exist_ok=True)
    os.makedirs(opt_dir, exist_ok=True)
    os.makedirs(apps_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)
    
    # Copy application files
    if os.path.exists("dist/TissueFragmentStitching"):
        shutil.copytree("dist/TissueFragmentStitching", opt_dir, dirs_exist_ok=True)
    
    # Create control file
    control_content = f'''Package: {pkg_name}
Version: {pkg_version}
Section: science
Priority: optional
Architecture: amd64
Depends: libc6, libgl1-mesa-glx
Maintainer: Scientific Imaging Lab <contact@example.com>
Description: Tissue Fragment Arrangement and Rigid Stitching
 Professional desktop application for visualizing, manipulating, and stitching
 multiple tissue image fragments from pyramidal TIFF files.
 .
 Features include high-resolution image support, interactive canvas,
 fragment manipulation, real-time updates, and export capabilities.
'''
    
    with open(f"{debian_dir}/control", 'w') as f:
        f.write(control_content)
    
    # Create desktop file
    desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=Tissue Fragment Stitching
Comment=Professional tissue fragment visualization and stitching
Exec=/opt/TissueFragmentStitching/TissueFragmentStitching
Icon=/opt/TissueFragmentStitching/icon.png
Terminal=false
Categories=Science;Education;Graphics;
StartupNotify=true
'''
    
    with open(f"{apps_dir}/tissue-fragment-stitching.desktop", 'w') as f:
        f.write(desktop_content)
    
    # Create symlink script
    postinst_content = '''#!/bin/bash
# Create symlink for command line access
ln -sf /opt/TissueFragmentStitching/TissueFragmentStitching /usr/local/bin/tissue-fragment-stitching
# Update desktop database
update-desktop-database /usr/share/applications
'''
    
    with open(f"{debian_dir}/postinst", 'w') as f:
        f.write(postinst_content)
    
    os.chmod(f"{debian_dir}/postinst", 0o755)
    
    # Create removal script
    prerm_content = '''#!/bin/bash
# Remove symlink
rm -f /usr/local/bin/tissue-fragment-stitching
'''
    
    with open(f"{debian_dir}/prerm", 'w') as f:
        f.write(prerm_content)
    
    os.chmod(f"{debian_dir}/prerm", 0o755)
    
    # Create build script
    build_deb_script = f'''#!/bin/bash
# Build .deb package

PKG_DIR="debian_package/{pkg_name}_{pkg_version}"

# Set permissions
find "$PKG_DIR" -type d -exec chmod 755 {{}} \\;
find "$PKG_DIR" -type f -exec chmod 644 {{}} \\;
chmod 755 "$PKG_DIR/opt/TissueFragmentStitching/TissueFragmentStitching"
chmod 755 "$PKG_DIR/DEBIAN/postinst"
chmod 755 "$PKG_DIR/DEBIAN/prerm"

# Build package
dpkg-deb --build "$PKG_DIR" "installers/{pkg_name}_{pkg_version}_amd64.deb"

echo "Debian package created: installers/{pkg_name}_{pkg_version}_amd64.deb"
'''
    
    with open('build_deb.sh', 'w') as f:
        f.write(build_deb_script)
    
    os.chmod('build_deb.sh', 0o755)
    
    print("Debian package structure created")
    print("To create .deb installer:")
    print("1. Run: ./build_deb.sh")
    print("2. The .deb file will be in the 'installers' folder")
    print("3. Users can install with: sudo dpkg -i package.deb")
    
    return True

def main():
    """Main build function"""
    print("=== Tissue Fragment Stitching Installer Builder ===")
    print("Creating simple click-to-install executables...\n")
    
    # Create installers directory
    os.makedirs('installers', exist_ok=True)
    
    # Install dependencies
    if not install_build_dependencies():
        print("❌ Failed to install build dependencies")
        return False
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable")
        return False
    
    # Create platform-specific installers
    system = platform.system().lower()
    
    print(f"\n=== Creating Installers for {system.title()} ===")
    
    if system == "windows":
        create_windows_installer()
    elif system == "darwin":
        create_macos_installer()
    else:  # Linux
        create_linux_installer()
    
    print("\n" + "="*50)
    print("🎉 BUILD COMPLETE!")
    print("="*50)
    print("\n📁 Files created:")
    print("   • dist/TissueFragmentStitching/ - Application files")
    
    if system == "windows":
        print("   • installer.iss - Inno Setup script")
        print("   • Future: installers/TissueFragmentStitching-Setup.exe")
    elif system == "darwin":
        print("   • dist/TissueFragmentStitching.app - macOS app bundle")
        print("   • create_dmg.sh - DMG creation script")
        print("   • Future: installers/TissueFragmentStitching-Installer.dmg")
    else:
        print("   • debian_package/ - Debian package structure")
        print("   • build_deb.sh - DEB creation script")
        print("   • Future: installers/tissue-fragment-stitching_1.0.0_amd64.deb")
    
    print("\n📋 Next steps:")
    if system == "windows":
        print("   1. Install Inno Setup from: https://jrsoftware.org/isinfo.php")
        print("   2. Open installer.iss in Inno Setup")
        print("   3. Click Build > Compile")
        print("   4. Share the .exe installer with users")
    elif system == "darwin":
        print("   1. Run: ./create_dmg.sh")
        print("   2. Share the .dmg installer with users")
    else:
        print("   1. Run: ./build_deb.sh")
        print("   2. Share the .deb installer with users")
    
    print("\n✨ Users will be able to:")
    print("   • Double-click the installer")
    print("   • Click Next > Next > Install")
    print("   • Launch from Start Menu/Applications")
    print("   • No Python or technical knowledge required!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)