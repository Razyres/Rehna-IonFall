# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller pour l'installeur IonFall (fichier .exe autonome)
# game.zip doit exister dans installer_src/ avant de lancer ce spec.

a = Analysis(
    ['installer_src/setup.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('installer_src/game.zip', '.'),
        ('site_web/images/IonFall_48x48.png', '.'),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pygame', 'pytmx', 'numpy'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

# Single-file exe : on inclut binaries/datas directement dans EXE (pas de COLLECT)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='IonFall_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='IonFall.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
