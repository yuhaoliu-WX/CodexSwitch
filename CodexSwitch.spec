# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

# 将项目根目录加入 sys.path，以便导入版本号
sys.path.insert(0, SPECPATH)
from core import __version__

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['customtkinter', 'pystray', 'PIL', 'yaml', 'winreg']
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('app')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('core', 'core'), ('app', 'app')],
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
    name=f'CodexSwitch-{__version__}-{platform.machine().lower()}',
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
)
