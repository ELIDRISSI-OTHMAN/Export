# 📦 Simple Installer Creation Guide

This guide shows you how to create **professional installers** that users can simply double-click to install your application - no Python knowledge required!

## 🚀 Quick Start

### 1. Run the Build Script
```bash
python build_installer.py
```

This will:
- ✅ Install all build tools automatically
- ✅ Create the executable 
- ✅ Generate installer scripts for your platform

### 2. Create the Final Installer

#### 🪟 **Windows** - Creates `.exe` installer
1. **Download Inno Setup**: https://jrsoftware.org/isinfo.php
2. **Install Inno Setup** (free)
3. **Open** `installer.iss` in Inno Setup
4. **Click** "Build" → "Compile"
5. **Done!** Your installer is in `installers/TissueFragmentStitching-Setup.exe`

#### 🍎 **macOS** - Creates `.dmg` installer
```bash
./create_dmg.sh
```
**Done!** Your installer is in `installers/TissueFragmentStitching-Installer.dmg`

#### 🐧 **Linux** - Creates `.deb` installer
```bash
./build_deb.sh
```
**Done!** Your installer is in `installers/tissue-fragment-stitching_1.0.0_amd64.deb`

## 📋 What Users Get

### Windows Users
- **Double-click** `TissueFragmentStitching-Setup.exe`
- **Click** "Next" → "Next" → "Install"
- **App appears** in Start Menu
- **Desktop shortcut** created
- **Uninstaller** in Add/Remove Programs

### macOS Users  
- **Double-click** `TissueFragmentStitching-Installer.dmg`
- **Drag app** to Applications folder
- **Launch** from Launchpad or Applications
- **Uninstall** by dragging to Trash

### Linux Users
- **Double-click** `tissue-fragment-stitching_1.0.0_amd64.deb`
- **Click** "Install Package"
- **App appears** in Applications menu
- **Uninstall** via package manager

## 🎯 Distribution

### File Sizes (Approximate)
- **Windows**: `TissueFragmentStitching-Setup.exe` (~150-300 MB)
- **macOS**: `TissueFragmentStitching-Installer.dmg` (~150-300 MB)  
- **Linux**: `tissue-fragment-stitching_1.0.0_amd64.deb` (~150-300 MB)

### Upload Locations
- **GitHub Releases** - Free hosting for open source
- **Your website** - Direct download links
- **Cloud storage** - Google Drive, Dropbox, etc.

## ✅ Features Included

### Professional Installation
- ✅ **Native installers** for each platform
- ✅ **Start Menu/Applications** integration
- ✅ **Desktop shortcuts** (optional)
- ✅ **File associations** (if needed)
- ✅ **Uninstaller** included
- ✅ **No Python required** for end users

### Bundled Dependencies
- ✅ **All Python packages** included
- ✅ **PyQt6** GUI framework
- ✅ **OpenCV** image processing
- ✅ **NumPy, SciPy** scientific computing
- ✅ **OpenSlide** pyramidal image support
- ✅ **All other dependencies** from requirements.txt

## 🔧 Customization

### Change App Name/Version
Edit these files:
- `build_installer.py` - Update version numbers
- `installer.iss` (Windows) - Update app info
- `create_dmg.sh` (macOS) - Update DMG name
- `build_deb.sh` (Linux) - Update package info

### Add App Icon
1. **Create** `icon.ico` (Windows), `icon.icns` (macOS), `icon.png` (Linux)
2. **Place** in project root
3. **Rebuild** installer

### Custom Install Location
- **Windows**: Edit `DefaultDirName` in `installer.iss`
- **macOS**: Users drag to Applications (standard)
- **Linux**: Edit paths in `build_deb.sh`

## 🐛 Troubleshooting

### Build Fails
```bash
# Install missing dependencies
pip install pyinstaller auto-py-to-exe

# Clean build
rm -rf build/ dist/ __pycache__/
python build_installer.py
```

### Large File Size
```bash
# Exclude unnecessary modules
# Edit app.spec and add to excludes:
excludes=[
    'tkinter',
    'matplotlib.tests',
    'numpy.tests',
    'scipy.tests',
]
```

### Missing Dependencies
```bash
# Add to hiddenimports in app.spec:
hiddenimports=[
    'your_missing_module',
]
```

## 📞 Support

### For Developers
- Check build logs for errors
- Test on clean systems without Python
- Verify all features work in built version

### For End Users
- Provide simple download links
- Include system requirements
- Offer basic troubleshooting guide

---

## 🎉 Result

Your users get a **professional software experience**:

1. **Download** installer from your website
2. **Double-click** to install  
3. **Click** through simple wizard
4. **Launch** from Start Menu/Applications
5. **Use** the app - no technical setup required!

**No Python, no command line, no technical knowledge needed!** ✨