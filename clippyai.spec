# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('.env', '.'),
        ('api', 'api'),
        ('ui', 'ui'),
    ],
    hiddenimports=[
        # Google AI
        'google.generativeai',
        'google.generativeai.client',
        'google.generativeai.types',
        
        # FastAPI & Uvicorn
        'fastapi',
        'fastapi.applications',
        'uvicorn',
        'uvicorn.main',
        'uvicorn.server',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        
        # Pydantic
        'pydantic',
        'pydantic.main',
        'pydantic.fields',
        
        # Other dependencies
        'markdown',
        'markdown.extensions',
        'markdown.extensions.fenced_code',
        'requests',
        'dotenv',
        'pyperclip',
        
        # PyQt5
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        
        # Standard library
        'subprocess',
        'json',
        'threading',
        'multiprocessing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClippyAI',
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
