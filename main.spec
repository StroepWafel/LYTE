# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Grab all PySide6 files (DLLs, plugins, etc.)
pyside6_datas, pyside6_binaries, pyside6_hiddenimports = collect_all('PySide6')

added_files = [
    ('Src/themes', 'themes'),  # Premade themes for EXE: dark/light/demo JSON, aurora_theme.qss, custom_theme.qss.demo
]

a = Analysis(
    ['Src\\main.py'],
    pathex=[],
    binaries=pyside6_binaries,
    datas=added_files + pyside6_datas,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'plyer.platforms.linux.notification',
        'plyer.platforms.darwin.notification',
        *pyside6_hiddenimports
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
    upx=False,
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
