"""
EDB: merge utility
------------------

This example shows how you can use the PyAEDT toolkit to create the WPF (Windows
Presentation Foundation) for Windows usage. It runs a merge between two
EDBs (package on board).
"""
######################################################################
# Download example
# ~~~~~~~~~~~~~~~~
#
# The example contains everything that you need to run it.
# You can customize the JSON file to change the settings.

import tempfile

from pyaedt.examples.downloads import download_edb_merge_utility

python_file = download_edb_merge_utility(force_download=True, destination=tempfile.gettempdir())
desktop_version = "2022.2"

######################################################################
# Launch Python script
# ~~~~~~~~~~~~~~~~~~~~
#
# You can launch a Python script in AEDT (**Tools->Run Script**) 
# or from the CPython command line.
#
# For this example, four items are downloaded:
#
# - ``package.aedb`` folder contains a package example.
# - ``board.aedb`` folder contains a board example.
# - ``merge_wizard.py`` file contains the Python script to run.
# - ``merge_wizard_settings.json`` file contains the settings.
#
# You can launch the ``merge_wizard.py`` file in AEDT (**Tools->Run Script**)
# or from the # CPython command line. This script works only on Windows with UI.
#
# The ``merge_wizard_settings.json`` file contains default settings that can be
# used in any other project to automatically load all settings.
#
# You can edit the following lines to launch a Python script from the Python
# interpreter:

# from pyaedt.generic.toolkit import launch
# launch(python_file, specified_version=desktop_version, new_desktop_session=False, autosave=False)
