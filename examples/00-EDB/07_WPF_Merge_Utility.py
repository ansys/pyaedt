"""
EDB: merge utility
------------------

This example shows how to use the PyAEDT toolkit to create WPF (Windows Presentation
Foundation) for Windows usage. It runs a merge between two EDBs (package on board).
"""

# sphinx_gallery_thumbnail_path = 'Resources/merge_utility.png'

######################################################################
# Download example
# ~~~~~~~~~~~~~~~~
#
# The example contains everything needed to run it.
# You can customize the JSON file to change the settings.

import tempfile

from pyaedt.examples.downloads import download_edb_merge_utility

python_file = download_edb_merge_utility(force_download=True, destination=tempfile.gettempdir())
desktop_version = "2022.2"

######################################################################
# Execute Python script
# ~~~~~~~~~~~~~~~~~~~~~
#
# The Python script can be launched in AEDT (Tools->Run Script) 
# or from the CPython command line.
# This example downloads four files:
#
# - ``package.aedb`` folder containing a package example
# - ``board.aedb`` folder containing a board example
# - ``merge_wizard.py`` file containing the Python script to run
# - ``merge_wizard_settings.json`` file containing the settings
#
# You can launch ``merge_wizard.py`` in AEDT (Tools->Run Script) or from the
# CPython command line. The script works only on Windows with UI.
#
# The JSON file contains default settings that can be used in any other project to automatically
# load all settings.
# You can edit the following lines to launch from the Python interpreter:

# from pyaedt.generic.toolkit import launch
# launch(python_file, specified_version=desktop_version, new_desktop_session=False, autosave=False)
