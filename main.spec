# -*- mode: python ; coding: utf-8 -*-

import os
import nicegui
import orjson
import pydantic_core
from PyInstaller.utils.hooks import collect_data_files

# Required files (manually added)
added_files = [
    ('src/icons/', 'icons'),
]

# Dynamically include the NiceGUI static files
nicegui_files = collect_data_files('nicegui', include_py_files=True)

# Binary C extensions for orjson and pydantic_core
binaries = [
    (orjson.__file__.replace('__init__.py', 'orjson.pyd'), 'orjson'),
    (pydantic_core.__file__.replace('__init__.py', '_pydantic_core.pyd'), 'pydantic_core'),
]

# Combine all data files
datas = added_files + nicegui_files

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'plyer.platforms.linux.notification',
        'plyer.platforms.darwin.notification',
        'orjson.orjson',
        'pydantic_core._pydantic_core',
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
    name='YTLM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico'
)
