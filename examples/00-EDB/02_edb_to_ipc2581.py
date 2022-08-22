"""
EDB: IPC2581 export
-------------------
This example shows how you can use PyAEDT to export an IPC2581 file.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes importing a section.

import shutil
import os
from pyaedt import generate_unique_name, examples, Edb, generate_unique_folder_name

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.


temp_folder = generate_unique_folder_name()

targetfile = os.path.dirname(examples.download_aedb(temp_folder))

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
# Parametrize a net.

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
