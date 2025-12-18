# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Don't Touch installer build (folder mode)."""

import sys
from pathlib import Path
import importlib.util

block_cipher = None

# Get the project root directory
project_root = Path(SPECPATH)

# Find package location
def get_package_path(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec and spec.origin:
        return Path(spec.origin).parent
    return None

customtkinter_path = get_package_path('customtkinter')
darkdetect_path = get_package_path('darkdetect')
mediapipe_path = get_package_path('mediapipe')

# Data files to include
datas = [
    (str(project_root / 'assets'), 'assets'),
    (str(project_root / 'locales'), 'locales'),
]

# Add package data files
if customtkinter_path:
    datas.append((str(customtkinter_path), 'customtkinter'))
if darkdetect_path:
    datas.append((str(darkdetect_path), 'darkdetect'))
if mediapipe_path:
    datas.append((str(mediapipe_path), 'mediapipe'))

# Hidden imports for MediaPipe and other dependencies
hiddenimports = [
    'mediapipe',
    'mediapipe.python',
    'mediapipe.python.solutions',
    'mediapipe.python.solutions.hands',
    'mediapipe.python.solutions.pose',
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'customtkinter',
    'darkdetect',
    'pystray',
    'pystray._win32',
    'tkinter',
    'tkinter.ttk',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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

# Folder-based EXE (not single file) for installer
exe = EXE(
    pyz,
    a.scripts,
    [],  # Don't bundle binaries into exe
    exclude_binaries=True,  # Keep binaries separate
    name='DontTouch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'icon.ico') if (project_root / 'assets' / 'icon.ico').exists() else None,
)

# Collect all files into a folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DontTouch',
)
