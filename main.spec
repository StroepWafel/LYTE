# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

added_files = [
    ('src/icons/', 'icons'),
]

nicegui_files = collect_data_files('nicegui', include_py_files=True)
orjson_binaries = collect_dynamic_libs('orjson')
pydantic_core_binaries = collect_dynamic_libs('pydantic_core')

binaries = orjson_binaries + pydantic_core_binaries
datas = added_files + nicegui_files

hiddenimports = collect_submodules('pydantic_core') + collect_submodules('orjson') + [
    'plyer.platforms.win.notification',
    'plyer.platforms.linux.notification',
    'plyer.platforms.darwin.notification',
]

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    icon='app.ico'
)
