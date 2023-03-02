"""
EDB: IPC2581 export
-------------------
This example shows how you can use PyAEDT to export an IPC2581 file.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports, which includes importing a section.

import os
import pyaedt

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.


temp_folder = pyaedt.generate_unique_folder_name()

targetfile = os.path.dirname(pyaedt.downloads.download_aedb(temp_folder))

ipc2581_file = os.path.join(temp_folder, "Galileo.xml")

print(targetfile)


###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyaedt.Edb` class, using EDB 2022 R2 and SI units.

edb = pyaedt.Edb(edbpath=targetfile, edbversion="2023.1")


###############################################################################
# Parametrize net
# ~~~~~~~~~~~~~~~
# Parametrize a net.

edb.core_primitives.parametrize_trace_width(
    "A0_N", parameter_name=pyaedt.generate_unique_name("Par"), variable_value="0.4321mm"
)

###############################################################################
# Cutout
# ~~~~~~
# Create a cutout.
signal_list = []
for net in edb.core_nets.nets.keys():
    if "PCIE" in net:
        signal_list.append(net)
power_list = ["GND"]
edb.create_cutout_multithread(signal_list=signal_list, reference_list=power_list, extent_type="ConvexHull",
                              expansion_size=0.002,
                              use_round_corner=False,
                              number_of_threads=4,
                              remove_single_pin_components=True,
                              use_pyaedt_extent_computing=True,
                              extent_defeature=0,
                              )

###############################################################################
# Plot cutout
# ~~~~~~~~~~~
# Plot cutout before exporting to IPC2581 file.

edb.core_nets.plot(None, None, color_by_net=True)

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
