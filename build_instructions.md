# Build Instructions for Tissue Fragment Stitching

This document provides detailed instructions for creating installers for the Tissue Fragment Stitching application.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Git (for version control)
- Platform-specific build tools (see below)

### Python Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller cx_freeze
```

### Platform-Specific Tools

#### Windows
- **NSIS** (Nullsoft Scriptable Install System): Download from https://nsis.sourceforge.io/
- **Visual Studio Build Tools** (for some Python packages)

#### macOS
- **Xcode Command Line Tools**: `xcode-select --install`
- **dmgbuild**: `pip install dmgbuild`

#### Linux
- **Standard build tools**: `sudo apt-get install build-essential`
- **FPM** (for advanced packaging): `gem install fpm`

## Quick Start

### Automated Build
```bash
python build_installer.py
```

This script will:
1. Install required build tools
2. Create executable using PyInstaller
3. Generate platform-specific installer

### Manual Build Steps

#### 1. Create Executable

**Using PyInstaller (Recommended):**
```bash
pyinstaller --clean --onedir --windowed \
    --add-data "src:src" \
    --add-data "README.md:." \
    --add-data "README_FR.md:." \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtOpenGLWidgets \
    --name TissueFragmentStitching \
    main.py
```

**Using cx_Freeze (Alternative):**
```bash
python setup_cx.py build
```

#### 2. Create Installer

**Windows:**
```bash
# After building executable
makensis installer.nsi
```

**macOS:**
```bash
# Create app bundle first, then
dmgbuild "Tissue Fragment Stitching" TissueFragmentStitching.dmg
```

**Linux:**
```bash
# Run the install script
chmod +x install.sh
./install.sh
```

## Build Options

### PyInstaller Options

#### One-File Executable
```bash
pyinstaller --onefile --windowed main.py
```
- **Pros**: Single executable file
- **Cons**: Slower startup, larger file size

#### One-Directory Bundle (Recommended)
```bash
pyinstaller --onedir --windowed main.py
```
- **Pros**: Faster startup, easier debugging
- **Cons**: Multiple files to distribute

### Advanced Configuration

#### Custom Icon
```bash
pyinstaller --icon=icon.ico main.py
```

#### Exclude Modules
```bash
pyinstaller --exclude-module tkinter main.py
```

#### Debug Mode
```bash
pyinstaller --debug=all main.py
```

## Platform-Specific Instructions

### Windows

#### Prerequisites
1. Install Python 3.8+
2. Install NSIS from https://nsis.sourceforge.io/
3. Install Visual Studio Build Tools

#### Build Process
```bash
# 1. Create virtual environment
python -m venv build_env
build_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 3. Build executable
pyinstaller tissue_fragment_stitching.spec

# 4. Create installer
makensis installer.nsi
```

#### Output
- `dist/TissueFragmentStitching/` - Application folder
- `TissueFragmentStitching-Setup.exe` - Windows installer

### macOS

#### Prerequisites
```bash
# Install Xcode command line tools
xcode-select --install

# Install dmgbuild
pip install dmgbuild
```

#### Build Process
```bash
# 1. Create virtual environment
python3 -m venv build_env
source build_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller dmgbuild

# 3. Build app bundle
pyinstaller --windowed --onedir main.py

# 4. Create DMG
dmgbuild "Tissue Fragment Stitching" TissueFragmentStitching.dmg
```

#### Output
- `dist/TissueFragmentStitching.app` - macOS application bundle
- `TissueFragmentStitching.dmg` - macOS disk image

### Linux

#### Prerequisites (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip build-essential
sudo apt-get install openslide-tools libgl1-mesa-glx
```

#### Build Process
```bash
# 1. Create virtual environment
python3 -m venv build_env
source build_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 3. Build executable
pyinstaller --onedir main.py

# 4. Create package
python build_installer.py
```

#### Output
- `dist/TissueFragmentStitching/` - Application folder
- `TissueFragmentStitching.desktop` - Desktop entry
- `install.sh` - Installation script

## Distribution

### File Structure
```
TissueFragmentStitching-1.0.0/
├── dist/
│   ├── TissueFragmentStitching/          # Application files
│   └── TissueFragmentStitching.exe       # Windows executable
├── TissueFragmentStitching-Setup.exe     # Windows installer
├── TissueFragmentStitching.dmg           # macOS installer
├── install.sh                           # Linux installer
└── README.md                            # Installation instructions
```

### Testing

#### Before Distribution
1. **Test on clean system** without Python installed
2. **Verify all dependencies** are included
3. **Test all features** work correctly
4. **Check file associations** (if applicable)
5. **Verify uninstaller** works properly

#### Test Commands
```bash
# Test executable directly
./dist/TissueFragmentStitching/TissueFragmentStitching

# Test installer
# Windows: Run TissueFragmentStitching-Setup.exe
# macOS: Mount TissueFragmentStitching.dmg
# Linux: Run ./install.sh
```

## Troubleshooting

### Common Issues

#### Missing Dependencies
```bash
# Add missing modules to PyInstaller
pyinstaller --hidden-import missing_module main.py
```

#### Large File Size
```bash
# Exclude unnecessary modules
pyinstaller --exclude-module matplotlib.tests main.py
```

#### Slow Startup
```bash
# Use onedir instead of onefile
pyinstaller --onedir main.py
```

#### OpenSlide Issues
```bash
# Windows: Ensure OpenSlide DLLs are included
# macOS: Install via Homebrew
# Linux: Install system package
```

### Debug Mode
```bash
# Run with debug output
pyinstaller --debug=all main.py

# Check generated executable
./dist/TissueFragmentStitching/TissueFragmentStitching --debug
```

## Automation

### GitHub Actions (CI/CD)
Create `.github/workflows/build.yml`:

```yaml
name: Build Installers

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller tissue_fragment_stitching.spec
      - uses: actions/upload-artifact@v3
        with:
          name: windows-build
          path: dist/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller --windowed main.py
      - uses: actions/upload-artifact@v3
        with:
          name: macos-build
          path: dist/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: sudo apt-get install openslide-tools libgl1-mesa-glx
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller main.py
      - uses: actions/upload-artifact@v3
        with:
          name: linux-build
          path: dist/
```

## Release Checklist

- [ ] Update version numbers in all files
- [ ] Test on all target platforms
- [ ] Create release notes
- [ ] Build all installers
- [ ] Test installers on clean systems
- [ ] Upload to distribution platform
- [ ] Update documentation
- [ ] Announce release

## Support

For build issues:
1. Check the build logs for errors
2. Verify all dependencies are installed
3. Test on the target platform
4. Check PyInstaller documentation
5. Create an issue with build logs