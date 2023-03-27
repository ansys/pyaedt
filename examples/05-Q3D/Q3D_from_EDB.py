"""
Q3D Extractor: PCB analysis
---------------------------
This example shows how you can use PyAEDT to create a design in
Q3D Extractor and run a simulation starting from an EDB Project.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.
import os
import tempfile
import pyaedt


###############################################################################
# Setup project files and path
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download of needed project file and setup of temporary project directory.
project_dir = tempfile.gettempdir()
aedb_project = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb')

project_name = pyaedt.generate_unique_name("HSD")
output_edb = os.path.join(project_dir, project_name + '.aedb')
output_q3d = os.path.join(project_dir, project_name + '_q3d.aedt')


###############################################################################
# Open EDB
# ~~~~~~~~
# Open the edb project and created a cutout on the selected nets
# before exporting to Q3D.
edb = pyaedt.Edb(aedb_project, edbversion="2023.1")
edb.create_cutout_multithread(["CLOCK_I2C_SCL", "CLOCK_I2C_SDA"], ["GND"], output_aedb_path=output_edb,
                              use_pyaedt_extent_computing=True, )


###############################################################################
# Identify pins position
# ~~~~~~~~~~~~~~~~~~~~~~
# Identify pins location on the components to define where to assign sources
# and sinks in Q3D.

pin_u13_scl = [i for i in edb.core_components.components["U13"].pins.values() if i.net_name == "CLOCK_I2C_SCL"]
pin_u1_scl = [i for i in edb.core_components.components["U1"].pins.values() if i.net_name == "CLOCK_I2C_SCL"]
pin_u13_sda = [i for i in edb.core_components.components["U13"].pins.values() if i.net_name == "CLOCK_I2C_SDA"]
pin_u1_sda = [i for i in edb.core_components.components["U1"].pins.values() if i.net_name == "CLOCK_I2C_SDA"]

location_u13_scl = [i * 1000 for i in pin_u13_scl[0].position[::]]
location_u13_scl.append(edb.core_components.components["U13"].upper_elevation * 1000)

location_u1_scl = [i * 1000 for i in pin_u1_scl[0].position[::]]
location_u1_scl.append(edb.core_components.components["U1"].upper_elevation * 1000)

location_u13_sda = [i * 1000 for i in pin_u13_sda[0].position[::]]
location_u13_sda.append(edb.core_components.components["U13"].upper_elevation * 1000)

location_u1_sda = [i * 1000 for i in pin_u1_sda[0].position[::]]
location_u1_sda.append(edb.core_components.components["U1"].upper_elevation * 1000)

###############################################################################
# Save and close Edb
# ~~~~~~~~~~~~~~~~~~
# Save, close Edb and open it in Hfss 3D Layout to generate the 3D model.

edb.save_edb()
edb.close_edb()

h3d = pyaedt.Hfss3dLayout(output_edb, specified_version="2023.1")

###############################################################################
# Export to Q3D
# ~~~~~~~~~~~~~
# Create a dummy setup and expor the layout in Q3D.
# keep_net_name will reassign Q3D nets names from Hfss 3D Layout.

setup = h3d.create_setup()
setup.export_to_q3d(output_q3d, keep_net_name=True)

h3d.close_project()
q3d = pyaedt.Q3d(output_q3d)

q3d.plot(show=False, export_path=os.path.join(q3d.working_directory, "Q3D.jpg"), plot_air_objects=False)

f1 = q3d.modeler.get_faceid_from_position(location_u13_scl)
q3d.assign_source_to_sheet(f1, "CLOCK_I2C_SCL")
f1 = q3d.modeler.get_faceid_from_position(location_u13_sda)
q3d.assign_source_to_sheet(f1, "CLOCK_I2C_SDA")
f1 = q3d.modeler.get_faceid_from_position(location_u1_scl)
q3d.assign_sink_to_sheet(f1, "CLOCK_I2C_SCL")
f1 = q3d.modeler.get_faceid_from_position(location_u1_sda)
q3d.assign_sink_to_sheet(f1, "CLOCK_I2C_SDA")
setup = q3d.create_setup()
setup.dc_enabled = True
setup.capacitance_enabled = False
setup.analyze()
sweep = setup.add_sweep()
sweep.add_subrange("LinearStep", 0, end=2, count=0.05, unit="GHz", save_single_fields=False, clear=True)
traces_acl = q3d.post.available_report_quantities(quantities_category="ACL Matrix")
traces_acr = q3d.post.available_report_quantities(quantities_category="ACR Matrix")
solution = q3d.post.get_solution_data(traces_acl)
solution.plot()

solution2 = q3d.post.get_solution_data(traces_acr)
solution2.plot()
q3d.release_desktop()
