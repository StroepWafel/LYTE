import dearpygui
import os
from PyInstaller.utils.hooks import collect_dynamic_libs

# Collect all dearpygui DLLs and binaries
dearpygui_binaries = collect_dynamic_libs('dearpygui')

added_files = [
    ('src/icons/', 'icons'),
]

# Add dearpygui DLLs to binaries
binaries = dearpygui_binaries

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=added_files,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'plyer.platforms.linux.notification',
        'plyer.platforms.darwin.notification'
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
