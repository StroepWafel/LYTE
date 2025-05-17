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

# Locate binary extensions correctly
orjson_pyd = collect_data_files('orjson', include_py_files=True)
pydantic_core_pyd = collect_data_files('pydantic_core', include_py_files=True)

def flatten_binaries(files):
    flat = []
    for src, dest in files:
        if isinstance(src, list):
            for s in src:
                flat.append((s, dest))
        else:
            flat.append((src, dest))
    return flat

binaries = flatten_binaries(orjson_pyd) + flatten_binaries(pydantic_core_pyd)


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
