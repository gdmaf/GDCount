# -*- mode: python ; coding: utf-8 -*-
#
# contador_graos.spec
#
# Como usar:
#   1. Ative seu ambiente virtual (grain-env)
#   2. Execute: pip install pyinstaller
#   3. Execute: pyinstaller contador_graos.spec
#   4. O .exe estará em: dist\ContadorGraos\ContadorGraos.exe
#
# IMPORTANTE: Coloque seg_model.keras e sam_vit_b_01ec64.pth
#             na mesma pasta que o ContadorGraos.exe gerado.

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# ─── Coleta automática de pacotes problemáticos ──────────────────────────────
datas_tf,     binaries_tf,     hiddenimports_tf     = collect_all('tensorflow')
datas_seg,    binaries_seg,    hiddenimports_seg     = collect_all('segmenteverygrain')
datas_sam,    binaries_sam,    hiddenimports_sam     = collect_all('segment_anything')
datas_ctk,    binaries_ctk,    hiddenimports_ctk     = collect_all('customtkinter')
datas_skimg,  binaries_skimg,  hiddenimports_skimg   = collect_all('skimage')

# rasterio — coleta completa para evitar ModuleNotFoundError
datas_rio,    binaries_rio,    hiddenimports_rio     = collect_all('rasterio')

# ─── Hidden imports manuais do rasterio (submodules que PyInstaller ignora) ──
rasterio_hidden = [
    'rasterio',
    'rasterio._base',
    'rasterio._features',
    'rasterio._filepath',
    'rasterio._shim',
    'rasterio._warp',
    'rasterio.control',
    'rasterio.coords',
    'rasterio.crs',
    'rasterio.drivers',
    'rasterio.dtypes',
    'rasterio.enums',
    'rasterio.env',
    'rasterio.errors',
    'rasterio.features',
    'rasterio.fill',
    'rasterio.io',
    'rasterio.mask',
    'rasterio.merge',
    'rasterio.plot',
    'rasterio.profiles',
    'rasterio.sample',
    'rasterio.shutil',
    'rasterio.transform',
    'rasterio.vrt',
    'rasterio.warp',
    'rasterio.windows',
]

# ─── Outros hidden imports comuns ────────────────────────────────────────────
extra_hidden = [
    'pkg_resources.py2_warn',
    'scipy._lib.messagestream',
    'scipy.special._ufuncs_cxx',
    'sklearn.utils._cython_blas',
    'sklearn.neighbors._typedefs',
    'sklearn.neighbors._quad_tree',
    'sklearn.tree._utils',
    'rtree',
    'shapely',
    'shapely.geometry',
    'shapely.ops',
    'PIL._imaging',
    'PIL.Image',
    'tqdm',
    'torch',
    'torchvision',
]

all_hidden = (
    rasterio_hidden
    + extra_hidden
    + hiddenimports_tf
    + hiddenimports_seg
    + hiddenimports_sam
    + hiddenimports_ctk
    + hiddenimports_skimg
    + hiddenimports_rio
)

all_datas = (
    datas_tf + datas_seg + datas_sam + datas_ctk + datas_skimg + datas_rio
)

all_binaries = (
    binaries_tf + binaries_seg + binaries_sam + binaries_ctk
    + binaries_skimg + binaries_rio
)

# ─── Análise ─────────────────────────────────────────────────────────────────
a = Analysis(
    ['app_contagem.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas + [('logo_gdmaf.png', '.'), ('GDcount.ico', '.')],
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib.tests',
        'IPython',
        'jupyter',
        'notebook',
    ],
    noarchive=False,
)

# ─── Pacote ──────────────────────────────────────────────────────────────────
pyz = PYZ(a.pure)

# ─── Executável ──────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ContadorGraos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # False = sem janela preta de terminal
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='GDcount.ico',            # Substitua por 'icone.ico' se quiser ícone personalizado
)

# ─── Pasta de distribuição ───────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ContadorGraos',
)
