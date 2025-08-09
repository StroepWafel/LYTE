# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Grab all Dear PyGui files (DLLs, pyd, etc.)
dpg_datas, dpg_binaries, dpg_hiddenimports = collect_all('dearpygui')

added_files = [
    ('src/icons/', 'icons'),
]

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=dpg_binaries,
    datas=added_files + dpg_datas,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'plyer.platforms.linux.notification',
        'plyer.platforms.darwin.notification',
        *dpg_hiddenimports
    ],
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
    a.binaries,
    a.datas,
    [],
    name='LYTE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico'
)
