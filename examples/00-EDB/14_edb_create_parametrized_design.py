# # EDB: parameterized design
#
# This example shows how to
# 1. Set up an HFSS project using SimulationConfiguration class.
# 2. Create automatically parametrized design.
#
# This image shows the layout created in this example:
#
# <img src="_static\parameterized_design.png" width="600">
#
#

# Import dependencies.

import os
import pyaedt
import tempfile

# Create an instance of a pyaedt.Edb object. 

# +
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
target_aedb = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_dir.name)
print("Project is located in ", target_aedb)

aedt_version = "2023.2"
edb = pyaedt.Edb(edbpath=target_aedb, edbversion=aedt_version)
print("AEDB file is located in {}".format(target_aedb))
# -

# ### Prepare the layout for the simulation
#
# The ``new_simulation_configuration()`` method creates an instance of 
# the ``SimulationConfiguration`` class. This class helps define all preprocessing steps
# required to set up the PCB for simulation. After the simulation configuration has been defined, 
# they are applied to the EDB using the ``Edb.build_simulation()`` method.

simulation_configuration = edb.new_simulation_configuration()
simulation_configuration.signal_nets = ["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N",
                                        "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N"]
simulation_configuration.power_nets = ["GND"]
simulation_configuration.components = ["X1", "U1"]
simulation_configuration.do_cutout_subdesign = True
simulation_configuration.start_freq = "OGHz"
simulation_configuration.stop_freq = "20GHz"
simulation_configuration.step_freq = "10MHz"

# Now apply the simulation setup to the EDB.

edb.build_simulation_project(simulation_configuration)

# ### Parameterize
#
# The layout can automatically be set up to enable parametric studies. For example, the
# impact of antipad diameter or trace width on signal integrity performance may be invested parametrically.

edb.auto_parametrize_design(layers=True, materials=True, via_holes=True, pads=True, antipads=True, traces=True)
edb.save_edb()
edb.close_edb()

# ## Open project in AEDT
#
# All manipulations thus far have been executed using the EDB API, which provides fast, streamlined processing of
# layout data in non-graphical mode. The layout and simulation setup can be visualized by opening it using the
# 3D Layout editor in AEDT.
#
# Note that there may be some delay while AEDT is being launched.

hfss = pyaedt.Hfss3dLayout(projectname=target_aedb, 
                           specified_version=aedt_version, 
                           non_graphical=False,
                           new_desktop_session=True)

# The following cell can be used to ensure that the design is valid for simulation.

validation_info = hfss.validate_full_design()
is_ready_to_simulate = True

# +
for s in validation_info[0]:
    if "error" in s:
        print(s)
        is_ready_to_simulate = False

if is_ready_to_simulate:
    print("The model is ready for simulation.")
else:
    print("There are errors in the model that must be fixed.")
# -

# ### Release the application from the Python kernel
#
# It is important to release the application from the Python kernel after 
# execution of the script. The default behavior of the ``release_desktop()`` method closes all open
# projects and closes the application.
#
# If you want to continue working on the project in graphical mode
# after script execution, call the following method with both arguments set to ``False``.

hfss.release_desktop(close_projects=True, close_desktop=True)
temp_dir.cleanup()  # Remove the temporary folder and files. All data will be removd!
