import glob
import os
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata
from ansys.aedt.core import is_linux

block_cipher = None

# path where this file is located
try:
    THIS_PATH = os.path.dirname(__file__)
except NameError:
    THIS_PATH = os.getcwd()

OUT_PATH = 'template_toolkit'
APP_NAME = 'template_toolkit' if is_linux else 'Template Toolkit'

CODE_PATH = os.path.join(THIS_PATH, 'src/ansys/aedt/toolkits/template')
INSTALLER_PATH = os.path.join(THIS_PATH, 'installer')
ASSETS_PATH = os.path.join(INSTALLER_PATH, 'assets')
ICON_FILE = os.path.join(ASSETS_PATH, 'splash_icon.ico')

# consider testing paths
main_py = os.path.join(CODE_PATH, 'run_toolkit.py')

if not os.path.isfile(main_py):
    raise FileNotFoundError(f'Unable to locate main entrypoint at {main_py}')

added_files = [
    (os.path.join(ASSETS_PATH, 'template.png'), 'assets'),
    (os.path.join(ASSETS_PATH, 'splash_icon.ico'), 'assets'),
    (os.path.join(INSTALLER_PATH, 'VERSION'), '.'),
]

# Missing metadata
added_files += copy_metadata('ansys-tools-visualization_interface')

if is_linux:
    added_files +=[(os.path.join(ASSETS_PATH, 'scripts'), 'assets')]

a = Analysis([main_py],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=['ansys.aedt.toolkits.template.backend.run_backend', 'ansys.aedt.toolkits.template.ui.run_frontend'],
             hookspath=['installer/hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=APP_NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon=ICON_FILE)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=OUT_PATH)
