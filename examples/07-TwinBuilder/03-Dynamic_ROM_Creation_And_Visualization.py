"""
Twin Builder: dynamic ROM creation and simulation (2023 R1 beta)
----------------------------------------------------------------
This example shows how you can use PyAEDT to create a dynamic ROM in Twin Builder
and run a Twin Builder time-domain simulation.

.. note::
    This example uses functionality only available in Twin Builder 2023 R1 and later.
    For 2023 R1, the build date must be 8/7/2022 or later. 
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import math
import shutil
import matplotlib.pyplot as plt
from pyaedt import TwinBuilder
from pyaedt import generate_unique_project_name
from pyaedt import generate_unique_folder_name
from pyaedt import examples

###############################################################################
# Select version and set launch options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select the Twin Builder version and set launch options. The following code
# launches Twin Builder 2023 R1 in graphical mode.
#
# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non-graphical mode. You can also change the Boolean parameter
# ``new_thread`` to ``False`` to launch Twin Builder in an existing AEDT session
# if one is running.

desktop_version = "2023.1"
non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
new_thread = True

###############################################################################
# Set up input data
# ~~~~~~~~~~~~~~~~~
# Define needed file name

source_snapshot_data_zipfilename = "Ex1_Mechanical_DynamicRom.zip"
source_build_conf_file = "dynarom_build.conf"

# Download data from example_data repository
temp_folder = generate_unique_folder_name()
source_data_folder = examples.download_twin_builder_data(source_snapshot_data_zipfilename, True, temp_folder)
source_data_folder = examples.download_twin_builder_data(source_build_conf_file, True, temp_folder)

# Toggle these for local testing 
# source_data_folder = "D:\\Scratch\\TempDyn"

data_folder = os.path.join(source_data_folder, "Ex03")

# Unzip training data and config file
examples.unzip(os.path.join(source_data_folder ,source_snapshot_data_zipfilename), data_folder)
shutil.copyfile(os.path.join(source_data_folder ,source_build_conf_file), os.path.join(data_folder,source_build_conf_file))


###############################################################################
# Launch Twin Builder and build ROM component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup for building the dynamic ROM component.

tb = TwinBuilder(projectname=generate_unique_project_name(),specified_version=desktop_version, non_graphical=non_graphical, new_desktop_session=new_thread)

# Get the dynamic ROM builder object
romMgr = tb._odesign.GetROMManager()
dromBuilder = romMgr.GetDynamicROMBuilder()

# Build the dynamic ROM with specified configuration file
confpath = os.path.join(data_folder,source_build_conf_file)
dromBuilder.Build(confpath.replace('\\', '/'))

# Test if ROM was created sucessfully
drompath = os.path.join(data_folder,'DynamicRom.dyn')
if os.path.exists(drompath):
	tb._odesign.AddMessage("Info","path exists: {}".format(drompath.replace('\\', '/')), "")
else:
	tb._odesign.AddMessage("Info","path does not exist: {}".format(drompath), "")

#Create the ROM component definition in Twin Builder
romMgr.CreateROMComponent(drompath.replace('\\', '/'),'dynarom') 


###############################################################################
# Create schematic
# ~~~~~~~~~~~~~~~~
# Place components to create a schematic.
 
# Define the grid distance for ease in calculations

G = 0.00254

# Place a dynamic ROM component

rom1 = tb.modeler.schematic.create_component("ROM1","","dynarom", [36 * G, 28 * G])

# Place two excitation sources

source1 = tb.modeler.schematic.create_periodic_waveform_source(None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 29 * G])
source2 = tb.modeler.schematic.create_periodic_waveform_source(None, "PULSE", 190, 0.002, "300deg", 210, 0, [20 * G, 25 * G])

# Connect components with wires

tb.modeler.schematic.create_wire([[22 * G, 29 * G], [33 * G, 29 * G]])
tb.modeler.schematic.create_wire([[22 * G, 25 * G], [30 * G, 25 * G], [30 * G, 28 * G], [33 * G, 28 * G]])

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

###############################################################################
# Parametrize transient setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("1000s")
tb.set_hmin("1s")
tb.set_hmax("1s")

###############################################################################
# Solve transient setup
# ~~~~~~~~~~~~~~~~~~~~~
# Solve the transient setup.

tb.analyze_setup("TR")


###############################################################################
# Get report data and plot using Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# output of the dynamic ROM.

E_Value = "PULSE1.VAL"
x = tb.post.get_solution_data(E_Value, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(E_Value))

T_Value = "ROM1.Temperature_history"
x = tb.post.get_solution_data(T_Value, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(T_Value))

plt.grid()
plt.xlabel("Time")
plt.ylabel("Temperature History Variation with Input Temperature Pulse")
plt.show()


###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulation is completed, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

# Clean up the downloaded data
shutil.rmtree(source_data_folder)

if os.name != "posix":
    tb.release_desktop()
