# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('src/ubw/libmpv-2.dll', '.')],
    datas=[('src/ubw/handlers/check_in_words.txt', 'ubw/handlers')],
    hiddenimports=['rich.logging', 'bilibili_api.clients.AioHTTPClient'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ubw',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ubw',
)
