# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

icon_path = 'assets/app_icon.ico' if os.path.exists('assets/app_icon.ico') else None

payload_path = os.path.abspath(os.path.join('dist', 'TPexcelApp'))
datas = []
if os.path.exists(payload_path):
    datas.append((payload_path, 'payload'))

uninstaller_path = os.path.abspath(os.path.join('dist', 'uninstall.exe'))
if os.path.exists(uninstaller_path):
    datas.append((uninstaller_path, '.'))

if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

a = Analysis(
    ['installer_wizard.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'winreg',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TPexcel_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=icon_path,
    disable_windowed_traceback=False,
)
