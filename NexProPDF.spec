# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_connected.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('resources', 'resources'), ('resources/tesseract', 'tesseract')],
    hiddenimports=[
        'pdf2docx', 'pdf2docx.converter', 'pdf2docx.page.Page', 'pdf2docx.page.Pages',
        'docx', 'docx.shared', 'docx.oxml', 'docx.oxml.ns', 'docx.document', 'docx.text.paragraph',
        'docx.enum.text', 'docx.enum.style',
        'fontTools', 'fontTools.ttLib', 'fontTools.subset',
        'numpy', 'cv2', 'fire',
        'pytesseract', 'PIL', 'PIL.Image',
        'PyKCS11', 'PyKCS11.LowLevel'
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
    [],
    exclude_binaries=True,
    name='NexProPDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/nexpro_pdf.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NexProPDF',
)
