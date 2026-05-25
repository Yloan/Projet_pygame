# -*- mode: python ; coding: utf-8 -*-
import sys as _sys

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['colorama', 'pygame', 'pygame.font', 'pygame.mixer', 'urllib.request'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

if _sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='BLITZKRIEG-Launcher',
        debug=False,
        strip=False,
        upx=False,
        console=False,
        argv_emulation=False,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name='BLITZKRIEG-Launcher',
    )
    app = BUNDLE(
        coll,
        name='BLITZKRIEG-Launcher.app',
        bundle_identifier='com.blitzkrieg.launcher',
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='BLITZKRIEG-Launcher',
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
    )
