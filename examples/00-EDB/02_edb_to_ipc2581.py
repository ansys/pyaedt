"""
Edb: IPC 2581 Export
--------------------
This example shows how to use PyAEDT to Export an IPC2581 file.
"""
# sphinx_gallery_thumbnail_path = 'Resources/ipc2581.png'


###############################################################################
# Import Section
# ~~~~~~~~~~~~~~
import shutil
import os
import tempfile
from pyaedt import generate_unique_name, examples, Edb

###############################################################################
# File download
# ~~~~~~~~~~~~~
# In this section the aedb file will be downloaded and copied in Temporary Folder.

tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
example_path = examples.download_aedb()
targetfolder = os.path.join(temp_folder, "Galileo.aedb")
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)
targetfile = os.path.join(targetfolder)
ipc2581_file = os.path.join(temp_folder, "Galileo.xml")

print(targetfile)


###############################################################################
# Launch EDB
# ~~~~~~~~~~
# This example launches the :class:`pyaedt.Edb` class.
# This example uses EDB 2022R2 and uses SI units.

edb = Edb(edbpath=targetfile, edbversion="2022.2")


###############################################################################
# Parametrize a Net

edb.core_primitives.parametrize_trace_width(
    "A0_N", parameter_name=generate_unique_name("Par"), variable_value="0.4321mm"
)

###############################################################################
# Create IPC2581 File

edb.export_to_ipc2581(ipc2581_file, "inch")
print("IPC2581 File has been saved to {}".format(ipc2581_file))

###############################################################################
# Close EDB

edb.close_edb()
