#!/usr/bin/env python3
"""
Build installer for Tissue Fragment Stitching application
This version includes debug output to help identify runtime issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("STDERR:", e.stderr)
        print("STDOUT:", e.stdout)
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def install_build_tools():
    """Install required build tools"""
    print("\n🔧 Installing build tools...")
    
    tools = [
        "pyinstaller",
        "auto-py-to-exe"
    ]
    
    for tool in tools:
        if not run_command([sys.executable, "-m", "pip", "install", tool], f"Installing {tool}"):
            print(f"⚠️  Failed to install {tool}, continuing anyway...")
    
    return True

def create_debug_spec():
    """Create PyInstaller spec file with debug options"""
    print("\n📝 Creating debug spec file...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, current_dir)

block_cipher = None

# Define all the data files and hidden imports
datas = [
    ('src', 'src'),
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

hiddenimports = [
    # Core PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    
    # Image processing
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'tifffile',
    'skimage',
    'skimage.feature',
    'skimage.transform',
    'skimage.measure',
    
    # Scientific computing
    'scipy',
    'scipy.optimize',
    'scipy.ndimage',
    
    # OpenSlide (if available)
    'openslide',
    
    # Application modules
    'src',
    'src.main_window',
    'src.core',
    'src.core.fragment',
    'src.core.fragment_manager',
    'src.core.image_loader',
    'src.core.labeled_point',
    'src.core.point_manager',
    'src.core.group_manager',
    'src.ui',
    'src.ui.canvas_widget',
    'src.ui.control_panel',
    'src.ui.fragment_list',
    'src.ui.toolbar',
    'src.ui.theme',
    'src.ui.export_dialog',
    'src.ui.point_input_dialog',
    'src.utils',
    'src.utils.export_manager',
    'src.utils.pyramidal_exporter',
    'src.algorithms',
    'src.algorithms.rigid_stitching',
]

# Collect binaries (DLLs)
binaries = []

a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
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
    debug=True,  # Enable debug output
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Show console for debug output
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
    
    with open('debug_app.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Debug spec file created")
    return True

def create_runtime_hook():
    """Create runtime hook for debugging"""
    print("\n🔗 Creating runtime hook...")
    
    hook_content = '''"""
Runtime hook for debugging import issues
"""
import sys
import os
import traceback

print("🚀 RUNTIME HOOK STARTED")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Print sys.path
print("\\n📁 Python path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Check if we're running as frozen
if hasattr(sys, '_MEIPASS'):
    print(f"\\n❄️  Running as frozen executable")
    print(f"Bundle directory: {sys._MEIPASS}")
    
    # Add bundle directory to path
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
        print(f"Added bundle directory to Python path")
else:
    print("\\n🐍 Running as Python script")

# Try to import critical modules
critical_modules = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'numpy',
    'cv2',
    'PIL',
    'tifffile'
]

print("\\n🔍 Testing critical imports:")
for module in critical_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")

# Try to import application modules
app_modules = [
    'src',
    'src.main_window',
    'src.core.fragment',
    'src.ui.canvas_widget'
]

print("\\n🏠 Testing application imports:")
for module in app_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        traceback.print_exc()

print("\\n🏁 RUNTIME HOOK COMPLETED")
'''
    
    with open('runtime_hook.py', 'w') as f:
        f.write(hook_content)
    
    print("✅ Runtime hook created")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🏗️  Building executable...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Build using spec file
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "debug_app.spec"]
    
    if not run_command(cmd, "Building executable with PyInstaller"):
        return False
    
    print("✅ Executable built successfully")
    return True

def create_test_script():
    """Create a test script to run the executable"""
    print("\n📋 Creating test script...")
    
    test_content = '''@echo off
echo ========================================
echo TESTING TISSUE FRAGMENT STITCHING
echo ========================================

cd /d "%~dp0"
echo Current directory: %CD%

echo.
echo Checking if executable exists...
if exist "dist\\TissueFragmentStitching\\TissueFragmentStitching.exe" (
    echo ✅ Executable found
) else (
    echo ❌ Executable not found
    pause
    exit /b 1
)

echo.
echo Running executable...
echo ========================================
"dist\\TissueFragmentStitching\\TissueFragmentStitching.exe"

echo.
echo ========================================
echo Execution completed
pause
'''
    
    with open('test_app.bat', 'w') as f:
        f.write(test_content)
    
    print("✅ Test script created: test_app.bat")
    return True

def main():
    """Main build process"""
    print("🚀 TISSUE FRAGMENT STITCHING - DEBUG BUILD")
    print("=" * 60)
    
    try:
        # Install build tools
        if not install_build_tools():
            print("❌ Failed to install build tools")
            return False
        
        # Create debug files
        if not create_runtime_hook():
            print("❌ Failed to create runtime hook")
            return False
            
        if not create_debug_spec():
            print("❌ Failed to create spec file")
            return False
        
        # Build executable
        if not build_executable():
            print("❌ Failed to build executable")
            return False
        
        # Create test script
        if not create_test_script():
            print("❌ Failed to create test script")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 NEXT STEPS:")
        print("1. Run 'test_app.bat' to test the executable")
        print("2. Check the console output for any errors")
        print("3. The executable is in: dist/TissueFragmentStitching/")
        print("\n💡 The executable will show a console window with debug info")
        print("   This will help us identify what's not working!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)