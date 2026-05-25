# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_game.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('sprite',              'sprite'),
        ('MAP',                 'MAP'),
        ('sound',               'sound'),
        ('game/assets/font',    'game/assets/font'),
    ],
    hiddenimports=['pytmx', 'pygame', 'pygame.font', 'pygame.mixer', 'pickle', 'xml.etree.ElementTree'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy', 'scipy', 'matplotlib', 'pandas',
        'tkinter', 'sqlite3', 'ssl', 'unittest',
        'email', 'html', 'http', 'urllib', 'pydoc',
        'doctest', 'difflib', 'logging', 'asyncio',
        'distutils', 'curses', 'multiprocessing.managers',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IonFall',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IonFall',
)
