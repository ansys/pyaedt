"""
Edb: Merge Utility
------------------

This example shows how to use pyaedt toolkit to create WPF for Windows usage.
This demo will show how to run a merge between two EDBs (eg. package on board).
"""

# sphinx_gallery_thumbnail_path = 'Resources/merge_utility.png'

######################################################################
# Download Example
# ~~~~~~~~~~~~~~~~
#
# Example contains everything to run.
# json fil can be customized to change settings.
import tempfile

from pyaedt.examples.downloads import download_edb_merge_utility

python_file = download_edb_merge_utility(force_download=True, destination=tempfile.gettempdir())
desktop_version = "2022.1"

######################################################################
# Python Script execution
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# Python file can be launched in Aedt or from CPython.
# This can be run from command line or from Run Script.
# The example downloads 4 files:
# - `package.aedb` folder containing a package example
# - `board.aedb` folder containing a board example
# - `merge_wizard.py` The python script to run
# - `merge_wizard_settings.json` json file containing settings
#
# User can launch `merge_wizard.py` from Aedt (Tools->Run Script) or from CPython.
# The script works only on windows with UI.
#
# The json file contains default settings that can be used in any other project to automatically
# load all settings.
# The following command line can be unchecked and launched from python interpreter.

# from pyaedt.generic.toolkit import launch
# launch(python_file, specified_version=desktop_version, new_desktop_session=False, autosave=False)
