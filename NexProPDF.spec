# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect ALL endesive submodules, data files, and binaries
endesive_datas, endesive_binaries, endesive_hiddenimports = collect_all('endesive')

a = Analysis(
    ['main_connected.py'],
    pathex=[],
    binaries=endesive_binaries,
    datas=[('config', 'config'), ('resources', 'resources'), ('resources/tesseract', 'tesseract')] + endesive_datas,
    hiddenimports=[
        'pdf2docx', 'pdf2docx.converter', 'pdf2docx.page.Page', 'pdf2docx.page.Pages',
        'docx', 'docx.shared', 'docx.oxml', 'docx.oxml.ns', 'docx.document', 'docx.text.paragraph',
        'docx.enum.text', 'docx.enum.style', 'docx.table', 'docx.text.run',
        'fontTools', 'fontTools.ttLib', 'fontTools.subset',
        'numpy', 'cv2', 'fire',
        'pytesseract', 'PIL', 'PIL.Image',
        'PyKCS11', 'PyKCS11.LowLevel',
        # asn1crypto (endesive dependency)
        'asn1crypto', 'asn1crypto.core', 'asn1crypto.cms', 'asn1crypto.x509',
        'asn1crypto.algos', 'asn1crypto.keys', 'asn1crypto.ocsp', 'asn1crypto.tsp',
        'asn1crypto.pem', 'asn1crypto.util',
        # cryptography (endesive dependency)
        'cryptography', 'cryptography.x509', 'cryptography.hazmat',
        'cryptography.hazmat.primitives', 'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.primitives.serialization.pkcs12',
        'cryptography.hazmat.primitives.hashes', 'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.backends', 'cryptography.hazmat.backends.openssl',
        # lxml (endesive dependency)
        'lxml', 'lxml.etree', 'lxml.objectify',
        # requests (endesive dependency for TSA/OCSP)
        'requests', 'requests.adapters', 'requests.auth', 'requests.structures',
        'urllib3', 'urllib3.util', 'urllib3.util.retry',
        'charset_normalizer', 'certifi', 'idna',
    ] + endesive_hiddenimports,
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
