import glob
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata
from PyInstaller import __main__

block_cipher = None

# Path where this script is located
try:
    THIS_PATH = os.path.dirname(__file__)
except NameError:
    THIS_PATH = os.getcwd()

OUT_PATH = 'pyaedt_bot'
APP_NAME = 'SAM Bot'

# Update paths based on the folder structure
CODE_PATH = os.path.join(THIS_PATH, "src", "ansys", "aedt", "core", "extensions", "pyaedt_bot")
INSTALLER_PATH = os.path.join(CODE_PATH, 'installer')
ASSETS_PATH = os.path.join(CODE_PATH, 'assets')
ICON_FILE = os.path.join(ASSETS_PATH, 'bot.ico')
HOOKS_DIR = os.path.join(INSTALLER_PATH, 'hooks')

# Path to the main entry file (pyaedt_bot.py)
main_py = os.path.join(CODE_PATH, 'pyaedt_bot.py')

if not os.path.isfile(main_py):
    raise FileNotFoundError(f'Unable to locate main entrypoint at {main_py}')

# Additional data files to include
added_files = [
    (os.path.join(ASSETS_PATH, 'bot.png'), 'assets'),
    (os.path.join(ASSETS_PATH, 'bot.ico'), 'assets'),
    (os.path.join(ASSETS_PATH, 'config.toml'), 'assets'),
    (os.path.join(INSTALLER_PATH, 'VERSION'), '.'),
]

# Copy required package metadata
added_files += copy_metadata('ansys-tools-visualization_interface')

# PyInstaller analysis
a = Analysis([main_py],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[HOOKS_DIR],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# Create the Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
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

# Collect all necessary files into the final output folder
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=OUT_PATH)
