# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('cpr/templates', 'cpr/templates'), ('Starting scripts', 'scripts')]
datas += copy_metadata('readchar')


a = Analysis(
    ['calibrated peer reviews.py'],
    pathex=['/Users/peteman/Documents/GitHub/CanvasPeerReviews'],
    binaries=[],
    datas=datas,
    hiddenimports=['readchar'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='calibrated peer reviews menu',
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
    name='calibrated peer reviews',
)
