@echo off
REM Don't Touch - Installer Build Script
REM Requires: Python, PyInstaller, Inno Setup

setlocal enabledelayedexpansion

echo ============================================
echo   Don't Touch - Installer Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Check if PyInstaller is available
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed
    echo Run: pip install pyinstaller
    exit /b 1
)

REM Check if Inno Setup is available
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "!ISCC!"=="" (
    echo [WARNING] Inno Setup not found. Will only build the application.
    echo Download from: https://jrsoftware.org/isdl.php
)

REM Clean previous builds
echo.
echo [1/4] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "installer_output" rmdir /s /q "installer_output"
echo Done.

REM Build with PyInstaller (folder mode for installer)
echo.
echo [2/4] Building application with PyInstaller...
pyinstaller build_installer.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    exit /b 1
)
echo Done.

REM Check if icon exists, create placeholder if not
if not exist "assets\icon.ico" (
    echo.
    echo [WARNING] assets\icon.ico not found
    echo Please add an icon file before creating the final installer.
)

REM Build installer with Inno Setup
if not "!ISCC!"=="" (
    echo.
    echo [3/4] Creating installer with Inno Setup...
    "!ISCC!" installer.iss
    if errorlevel 1 (
        echo [ERROR] Inno Setup build failed
        exit /b 1
    )
    echo Done.

    echo.
    echo [4/4] Build completed successfully!
    echo.
    echo Output files:
    echo   - Application: dist\DontTouch\DontTouch.exe
    echo   - Installer:   installer_output\DontTouch_Setup_*.exe
) else (
    echo.
    echo [3/4] Skipping installer creation (Inno Setup not found)
    echo.
    echo [4/4] Build completed!
    echo.
    echo Output files:
    echo   - Application: dist\DontTouch\DontTouch.exe
    echo.
    echo To create installer, install Inno Setup and run this script again.
)

echo.
echo ============================================
pause
