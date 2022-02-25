"""
Merge Utility
-------------
This example shows how to use pyaedt toolkit to create WPF for Windows usage.
This demo will show how to run a merge between two EDBs (eg. package on board).
"""
# sphinx_gallery_thumbnail_path = 'Resources/merge_utility.png'

######################################################################
# Download Example
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# Example contains everything to run.
# json fil can be customized to change settings.

from pyaedt.examples.downloads import download_edb_merge_utility

python_file = download_edb_merge_utility()


######################################################################
# Python Script execution
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# # Python file can be launched in AEDT or from CPython.
# This can be run from command line or from Run Script.
