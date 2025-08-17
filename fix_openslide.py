#!/usr/bin/env python3
"""
Fix OpenSlide DLL issues for Windows builds
Run this script if you're having OpenSlide problems
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def find_openslide_dlls():
    """Find OpenSlide DLL files"""
    try:
        import openslide
        openslide_path = Path(openslide.__file__).parent
        
        # Common locations for OpenSlide DLLs
        possible_paths = [
            openslide_path / "bin",
            openslide_path / "_bin",
            openslide_path.parent / "openslide" / "bin",
            Path(sys.prefix) / "Library" / "bin",  # Conda
            Path(sys.prefix) / "Lib" / "site-packages" / "openslide" / "bin",
        ]
        
        dll_files = []
        for path in possible_paths:
            if path.exists():
                dlls = list(path.glob("*.dll"))
                if dlls:
                    print(f"Found OpenSlide DLLs in: {path}")
                    dll_files.extend(dlls)
                    break
        
        return dll_files
        
    except ImportError:
        print("OpenSlide not installed")
        return []

def copy_openslide_dlls_to_dist():
    """Copy OpenSlide DLLs to distribution folder"""
    dist_path = Path("dist/TissueFragmentStitching")
    if not dist_path.exists():
        print("Distribution folder not found. Build the executable first.")
        return False
    
    dll_files = find_openslide_dlls()
    if not dll_files:
        print("No OpenSlide DLLs found")
        return False
    
    # Create openslide_bin directory
    openslide_bin = dist_path / "openslide_bin"
    openslide_bin.mkdir(exist_ok=True)
    
    # Copy DLL files
    copied_count = 0
    for dll_file in dll_files:
        dest = openslide_bin / dll_file.name
        try:
            shutil.copy2(dll_file, dest)
            print(f"Copied: {dll_file.name}")
            copied_count += 1
        except Exception as e:
            print(f"Failed to copy {dll_file.name}: {e}")
    
    print(f"✓ Copied {copied_count} OpenSlide DLLs")
    return copied_count > 0

def install_openslide_windows():
    """Install OpenSlide for Windows"""
    print("Installing OpenSlide for Windows...")
    
    # Try different installation methods
    methods = [
        # Method 1: pip install
        [sys.executable, "-m", "pip", "install", "openslide-python", "--force-reinstall"],
        # Method 2: conda install (if conda is available)
        ["conda", "install", "-c", "conda-forge", "openslide-python", "-y"],
    ]
    
    for method in methods:
        try:
            result = subprocess.run(method, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ OpenSlide installed successfully using: {method[0]}")
                return True
        except FileNotFoundError:
            continue
    
    print("❌ Failed to install OpenSlide automatically")
    print("\nManual installation options:")
    print("1. Download OpenSlide from: https://openslide.org/download/")
    print("2. Install using conda: conda install -c conda-forge openslide-python")
    print("3. Use pre-compiled wheels: pip install openslide-python")
    
    return False

def create_openslide_hook():
    """Create PyInstaller hook for OpenSlide"""
    hook_content = '''# PyInstaller hook for OpenSlide
import os
import sys
from pathlib import Path

def get_openslide_binaries():
    """Get OpenSlide binary files"""
    binaries = []
    
    try:
        import openslide
        openslide_path = Path(openslide.__file__).parent
        
        # Look for DLL files
        possible_paths = [
            openslide_path / "bin",
            openslide_path / "_bin",
            openslide_path.parent / "openslide" / "bin",
        ]
        
        for path in possible_paths:
            if path.exists():
                for dll_file in path.glob("*.dll"):
                    binaries.append((str(dll_file), "openslide_bin"))
                break
                
    except ImportError:
        pass
    
    return binaries

# PyInstaller hook variables
binaries = get_openslide_binaries()
hiddenimports = ['openslide._convert', 'openslide.lowlevel']
'''
    
    # Create hooks directory
    hooks_dir = Path("hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    hook_file = hooks_dir / "hook-openslide.py"
    with open(hook_file, 'w') as f:
        f.write(hook_content)
    
    print(f"✓ Created PyInstaller hook: {hook_file}")
    return True

def main():
    """Main function"""
    print("=== OpenSlide Fix Tool ===")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        # Install OpenSlide
        if sys.platform == "win32":
            install_openslide_windows()
        else:
            print("This script is for Windows. On other platforms:")
            print("- macOS: brew install openslide")
            print("- Linux: sudo apt-get install openslide-tools")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--copy":
        # Copy DLLs to existing build
        copy_openslide_dlls_to_dist()
        return
    
    # Default: show information and create hook
    print("\n1. Checking OpenSlide installation...")
    dll_files = find_openslide_dlls()
    
    if dll_files:
        print(f"✓ Found {len(dll_files)} OpenSlide DLL files")
        for dll in dll_files:
            print(f"  - {dll}")
    else:
        print("❌ No OpenSlide DLLs found")
        print("\nRun with --install to install OpenSlide")
        return
    
    print("\n2. Creating PyInstaller hook...")
    create_openslide_hook()
    
    print("\n3. Next steps:")
    print("   - Rebuild your executable: python build_installer.py")
    print("   - Or copy DLLs to existing build: python fix_openslide.py --copy")

if __name__ == "__main__":
    main()