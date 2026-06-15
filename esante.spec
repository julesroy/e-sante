# esante.spec — racine du projet C:\source\e-sante\
# Lancer avec : pyinstaller esante.spec --clean --noconfirm

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None
ROOT = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, 'assets'),  'assets'),
        (os.path.join(ROOT, 'manuel'),  'manuel'),
        (os.path.join(ROOT, 'utils'),   'utils'),
        (os.path.join(ROOT, 'server'),  'server'),
    ],
    hiddenimports=[
        # --- PostgreSQL ---
        'psycopg2',
        'psycopg2.extensions',
        'psycopg2.extras',

        # --- Dotenv ---
        'dotenv',
        'python_dotenv',

        # --- OpenCV ---
        'cv2',

        # --- Numpy ---
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',

        # --- Scipy ---
        'scipy',
        'scipy.ndimage',
        'scipy.ndimage._filters',
        'scipy.ndimage._interpolation',
        'scipy.ndimage._morphology',
        'scipy.ndimage._measurements',

        # --- Scikit-image (watershed) ---
        'skimage',
        'skimage.morphology',
        'skimage.segmentation',
        'skimage.feature',
        'skimage.filters',
        'skimage.measure',

        # --- Pydicom ---
        'pydicom',
        'pydicom.encoders',
        'pydicom.data',

        # --- Pillow ---
        'PIL',
        'PIL.Image',
        'PIL.ImageOps',

        # --- Requests ---
        'requests',
        'urllib3',
        'charset_normalizer',
        'certifi',
        'idna',

        # --- PyQt6 ---
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',

        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg',   # PyQt6
        'matplotlib.figure',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Serveur FastAPI — pas besoin dans l'exe client
        'fastapi',
        'uvicorn',
        'starlette',
        'pydantic',
        # Outils de dev inutiles dans l'exe
        'pytest',
        'black',
        'mypy_extensions',
        'pdoc',
        'invoke',
        'IPython',
        'jupyter',
        'tkinter',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PixelMed',
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
    icon=os.path.join(ROOT, 'assets', 'icons', 'app_icon.png'),
)