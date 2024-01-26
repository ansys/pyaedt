"""
# EDB: SIwave DC-IR Analysis

This example demonstrates the use of EDB to interact with a PCB
layout and run DC-IR analysis in SIwave.
"""
###############################################################################
# Perform required imports

import os
import time
import pyaedt
import tempfile

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
targetfile = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', 
                                            destination=temp_dir.name)

siwave_file = os.path.join(os.path.dirname(targetfile), "ANSYS-HSD_V1.siw")
print(targetfile)
aedt_file = targetfile[:-4] + "aedt"

###############################################################################
# ## Electronics Database (EDB)
#
# Instantiate an instance of the `pyaedt.Edb` class 
# using EDB 2023 R2 and SI units.
edb_version = "2023.2"
if os.path.exists(aedt_file):
    os.remove(aedt_file)
edb = pyaedt.Edb(edbpath=targetfile, edbversion=edb_version)

###############################################################################
# ## Identify nets and components
#
# The ``Edb.nets.netlist`` and ``Edb.components.components`` propreties contain information
# about all of the nets and components. The following cell uses this information to print the number of nets and components.

print("Nets {}".format(len(edb.nets.netlist)))
start = time.time()
print("Components {}".format(len(edb.components.components.keys())))
print("elapsed time = ", time.time() - start)

###############################################################################
# ## Identify Pin Positions
#
# The next section shows how to obtain all pins for a specific component and
# print the ``[x, y]`` position of each pin.

pins = edb.components["U2"].pins
count = 0
for pin in edb.components["U2"].pins.values():
    if count < 10:  # Only print the first 10 pin coordinates.
        print(pin.position)
    elif count == 10:
        print("...and many more.")
    else:
        pass
    count += 1

###############################################################################
# Get all nets connected to a specific component. Print
# the pin and the name of the net to which it is connected.

connections = edb.components.get_component_net_connection_info("U2")
n_print = 0 # Counter to limite the number of printed lines.
print_max = 15
for m in range(len(connections["pin_name"])):
    ref_des = connections["refdes"][m]
    pin_name = connections["pin_name"][m]
    net_name = connections["net_name"][m]
    if net_name != "" and (n_print < print_max):
        print("{}, pin {} -> net \"{}\"".format(ref_des, pin_name, net_name))
        n_print += 1
    elif n_print == print_max:
        print("...and many more.")
        n_print += 1

###############################################################################
# Compute rats.

rats = edb.components.get_rats()

###############################################################################
# ## Idenify Connected Nets
#
# The method ``get_dcconnected_net_list()`` retrieves a list of 
# all DC-connected power nets. Each group of connected nets is returned
# as a [set](https://docs.python.org/3/tutorial/datastructures.html#sets)
# The first argument to the method is the list of ground nets which will
# not be considered in the search for connected nets.

GROUND_NETS = ["GND", "GND_DP"]
dc_connected_net_list = edb.nets.get_dcconnected_net_list(GROUND_NETS)
for pnets in dc_connected_net_list:
    print(pnets)

###############################################################################
# ## Power Tree
#
# The power tree provides connectivity through all components from the VRM to
# the device.  

VRM = "U1"
OUTPUT_NET = "AVCC_1V3"
powertree_df, component_list_columns, net_group = edb.nets.get_powertree(OUTPUT_NET, GROUND_NETS)

###############################################################################
# Print some information about the power tree.

print_columns = ["refdes", "pin_name", "component_partname"]
ncol = [component_list_columns.index(c) for c in print_columns]

# This prints the header. Replace "pin_name" with "pin" to 
# make the header align with the values.
print("\t".join(print_columns).replace("pin_name", "pin"))

for el in powertree_df:
    s = ""
    count = 0
    for e in el:
        if count in ncol:
            s += "{}\t".format(e)
        count += 1
    s.rstrip()
    print(s)

###############################################################################
# ## Remove Unused Components
#
# Delete all RLC components that are connected with only one pin. 
# The method ``Edb.components.delete_single_pin_rlc()``
# provides a useful way to
# remove components that are not needed for the simulation.

edb.components.delete_single_pin_rlc()

###############################################################################
# Unused components can also be removed explicitly by name.

edb.components.delete("C380")

###############################################################################
# Nets can also be removed explicitly. 

edb.nets.delete("PDEN")

###############################################################################
# Print the top and bottom
# elevation of the stackup obtained using 
# the method ``Edb.stackup.limits()``.

s = "Top layer name: \"{top}\", Elevation: {top_el:.2f} "
s += "mm\nBottom layer name: \"{bot}\", Elevation: {bot_el:2f} mm"
top, top_el, bot, bot_el = edb.stackup.limits()
print(s.format(top = top, top_el = top_el*1E3, bot = bot, bot_el = bot_el*1E3))

###############################################################################
# ## Setup for SIwave DCIR analysis
#
# Create a voltage source and then set up a DCIR analysis.

edb.siwave.create_voltage_source_on_net("U1", "AVCC_1V3", "U1", "GND", 1.3, 0, "V1")
edb.siwave.create_current_source_on_net("IC2", "NetD3_2", "IC2", "GND", 1.0, 0, "I1")
setup = edb.siwave.add_siwave_dc_analysis("myDCIR_4")
setup.use_dc_custom_settings = True
setup.set_dc_slider = 0
setup.add_source_terminal_to_ground("V1", 1)

###############################################################################
# ## Solve
#
# Save the modifications and run the analysis in SIwave.

edb.save_edb()
edb.nets.plot(None, "1_Top",plot_components_on_top=True)

siw_file = edb.solve_siwave()

###############################################################################
# ## Export Results
#
# Export all quantities calculated from the DC-IR analysis. The following method runs SIwave in batch mode from the command line. Results are written to the edb folder.
outputs = edb.export_siwave_dc_results(siw_file, setup.name, )

###############################################################################
# Close the EDB. After EDB is closed, it can be opened by AEDT.

edb.close_edb()

###############################################################################
# ## View Layout in SIwave
#
# The SIwave user interface can be visualized and manipulated
# using the SIwave user interface. This command works on Window OS only.

# siwave = pyaedt.Siwave("2023.2")
# siwave.open_project(siwave_file)
# report_file = os.path.join(temp_folder,'Ansys.htm')
#
# siwave.export_siwave_report("myDCIR_4", report_file)
# siwave.close_project()
# siwave.quit_application()

###############################################################################
# Clean up the temporary files and directory.

temp_dir.cleanup()

""

