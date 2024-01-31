# # EDB: IPC2581 export
#
# This example shows how you can use PyAEDT to export an IPC2581 file.
#
# Perform required imports, which includes importing a section.

import os
import pyaedt
import tempfile

# Download the AEDB file and copy it in the temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
targetfile = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', 
                                            destination=temp_dir.name)
ipc2581_file_name = os.path.join(temp_dir.name, "Ansys_Hsd.xml")
print(targetfile)

# ## Launch EDB
#
# Launch the `pyaedt.Edb` class, using Verson 2023. 
# > Note that length dimensions passed to Edb are in SI units.

edb = pyaedt.Edb(edbpath=targetfile, edbversion="2023.2")

# Parametrize the width of a trace.

edb.modeler.parametrize_trace_width(
    "A0_N", parameter_name=pyaedt.generate_unique_name("Par"), variable_value="0.4321mm"
)

# Create a cutout and plot it.

signal_list = []
for net in edb.nets.netlist:
    if "PCIe" in net:
        signal_list.append(net)
power_list = ["GND"]
edb.cutout(signal_list=signal_list, reference_list=power_list, extent_type="ConvexHull",
           expansion_size=0.002,
           use_round_corner=False,
           number_of_threads=4,
           remove_single_pin_components=True,
           use_pyaedt_extent_computing=True,
           extent_defeature=0,
           )
edb.nets.plot(None, None, color_by_net=True)

# Export the EDB to IPC2581 file.

edb.export_to_ipc2581(ipc2581_file_name, "inch")
print("IPC2581 File has been saved to {}".format(ipc2581_file_name))

# Close EDB

edb.close_edb()

# Clean up the temporary directory

temp_dir.cleanup()
