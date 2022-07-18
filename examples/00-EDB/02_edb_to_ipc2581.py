"""
EDB: IPC2581 export
-------------------
This example shows how to use PyAEDT to export an IPC2581 file.
"""
# sphinx_gallery_thumbnail_path = 'Resources/ipc2581.png'


###############################################################################
# Import section
# ~~~~~~~~~~~~~~
# Import a section.


import shutil
import os
import tempfile
from pyaedt import generate_unique_name, examples, Edb

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.


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
# Launch the :class:`pyaedt.Edb` class, using EDB 2022 R2 and SI units.

edb = Edb(edbpath=targetfile, edbversion="2022.2")


###############################################################################
# Parametrize net
# ~~~~~~~~~~~~~~~
# Parameterize a net.

edb.core_primitives.parametrize_trace_width(
    "A0_N", parameter_name=generate_unique_name("Par"), variable_value="0.4321mm"
)

###############################################################################
# Create IPC2581 file
# ~~~~~~~~~~~~~~~~~~~
# Create the IPC2581 file.

edb.export_to_ipc2581(ipc2581_file, "inch")
print("IPC2581 File has been saved to {}".format(ipc2581_file))

###############################################################################
# Close EDB
# ~~~~~~~~~
# Close EDB.

edb.close_edb()
