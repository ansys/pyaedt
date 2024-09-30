"""
Twin Builder: LTI ROM creation and simulation
----------------------------------------------------------------
This example shows how you can use PyAEDT to create a Linear Time Invariant (LTI) ROM in Twin Builder
and run a Twin Builder time-domain simulation. Inputs data are defined using Datapairs blocks with CSV files.

.. note::
    This example uses functionality only available in Twin Builder 2025 R1 and later.
"""
import datetime
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import shutil
import subprocess
import matplotlib.pyplot as plt
from ansys.aedt.core import TwinBuilder
from ansys.aedt.core import generate_unique_project_name
from ansys.aedt.core.generic.general_methods import generate_unique_folder_name
from ansys.aedt.core import downloads
from ansys.aedt.core.modeler.circuits.object_3d_circuit import CircuitPins

##########################################################
# Set AEDT version
# ~~~~~~~~~~~~~~~~
# Set AEDT version.

aedt_version = "2025.1"

###############################################################################
# Select version and set launch options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select the Twin Builder version and set launch options. The following code
# launches Twin Builder in graphical mode.
#
# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non-graphical mode. You can also change the Boolean parameter
# ``new_thread`` to ``False`` to launch Twin Builder in an existing AEDT session
# if one is running.

non_graphical = False
new_thread = True

###############################################################################
# Set up input data
# ~~~~~~~~~~~~~~~~~
# Define training data folder

training_data_folder = "LTI_training_data.zip"

# Download data from example_data repository
temp_folder = generate_unique_folder_name()
source_data_folder = downloads.download_twin_builder_data(training_data_folder, True, temp_folder)

data_folder = os.path.join(source_data_folder, "LTI_training")

# Unzip training data and parse ports names
downloads.unzip(os.path.join(source_data_folder, training_data_folder), data_folder)
ports_names_file = "Input_PortNames.txt"

def get_ports_info(ports_file):
    with open(ports_file, 'r') as PortNameFile:
        My_s = ""

        line = PortNameFile.readline()
        line_list = list(line.split())
        for i in range(len(line_list)):
            My_s += "Input" + str(i+1) + "_" + line_list[i] + ","

        line = PortNameFile.readline()
        line_list = list(line.split())
        for i in range(len(line_list)):
            My_s += "Output" + str(i+1) + "_" + line_list[i] + ","
        My_s = My_s[:- 1]

    return My_s

My_s = get_ports_info(os.path.join(data_folder, ports_names_file))

###############################################################################
# Launch Twin Builder and build ROM component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup for building the ROM component.

tb = TwinBuilder(project=generate_unique_project_name(),
                 version=aedt_version,
                 non_graphical=non_graphical,
                 new_desktop=new_thread)

# Switch the current desktop configuration and the schematic environment to "Twin Builder".
# This and the restoring section at the end are not needed if the desktop is already configured as "Twin Builder".
desktop = tb.odesktop
current_desktop_config = desktop.GetDesktopConfiguration()
current_schematic_environment = desktop.GetSchematicEnvironment()
desktop.SetDesktopConfiguration("Twin Builder")
desktop.SetSchematicEnvironment(1)

# Build the LTI ROM with specified configuration file
install_dir = desktop.GetRegistryString("Desktop/InstallationDirectory")
fitting_exe = os.path.join(install_dir, 'FittingTool.exe')
path = '\"'+ fitting_exe+ '\"' + "  " + '\"t\"' + "  " + '\"'+data_folder+'\"'
process = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
tb.logger.info("Fitting the LTI ROM training data")
exec = True
startTime = datetime.datetime.now()
execTime = 0.0
while exec and execTime < 60.0: # limiting the fitting process execution time to 1 minute
    out, err = process.communicate()
    execTime = (datetime.datetime.now()-startTime).total_seconds()
    if 'An LTI ROM has been generated' in str(out):
        process.terminate()
        exec = False

rom_file = ''

for i in os.listdir(data_folder):
    if i.endswith(".sml"):
        model_name_sml = i.split('.')[0]
        rom_file = os.path.join(data_folder, i)

if os.path.exists(rom_file):
    tb.logger.info("Built intermediate ROM file successfully at: %s", rom_file)
else:
    tb.logger.info("ROM file does not exist at the expected location : %s", rom_file)

# Import the ROM component model in Twin Builder
project = desktop.GetActiveProject()
design = project.GetActiveDesign()
defManager = project.GetDefinitionManager()
compManager = defManager.GetManager("Component")
editor = design.SetActiveEditor("SchematicEditor")
response = compManager.ImportModelsFromFile(rom_file,
		  	   [
		  		  "NAME:Options",
		  		  "Mode:="		, 1,
		  		  [
		  		     "NAME:Models",
		  			  model_name_sml + ":="	, [True]
		  		  ],
		  		  [
		  			 "NAME:Components",
                      model_name_sml + ":="	, [True,True,model_name_sml,True,My_s.lower(),My_s.lower()]
		  		  ]
		  	   ])

os.remove(rom_file)
if response:
    tb.logger.info("Import failed: %s", format(response))
else:
    tb.logger.info("LTI ROM model successfully imported")


# ###############################################################################
# Create schematic
# ~~~~~~~~~~~~~~~~
# Place components to create a schematic.

# Define the grid distance for ease in calculations

G = 0.00254

# Place the ROM component
rom1 = tb.modeler.schematic.create_component("ROM1", "", model_name_sml, [36 * G, 28 * G])

# Place Datapairs blocks for inputs definition
source1 = tb.modeler.schematic.create_component("source1","",
                                                "Simplorer Elements\\Basic Elements\\Tools\\Time Functions:DATAPAIRS",
                                                [20 * G, 29 * G])
source2 = tb.modeler.schematic.create_component("source2","",
                                                "Simplorer Elements\\Basic Elements\\Tools\\Time Functions:DATAPAIRS",
                                                [20 * G, 25 * G])

# Import Datasets
project.ImportDataset(os.path.join(data_folder,"data1.csv"))
project.ImportDataset(os.path.join(data_folder,"data2.csv"))
editor.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:PassedParameterTab",
			[
				"NAME:PropServers",
				editor.GetCompInstanceFromInstanceName("source1").GetPropServerName()
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:CH_DATA",
					"OverridingDef:="	, True,
					"Value:="		, "$input1"
				]
			]
		],
		[
			"NAME:Quantities",
			[
				"NAME:PropServers",
				editor.GetCompInstanceFromInstanceName("source1").GetPropServerName()
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:PERIO",
					"OverridingDef:="	, True,
					"Value:="		, "0",
					"NetlistUnits:="	, "",
					"ShowPin:="		, False,
					"Display:="		, False,
					"Sweep:="		, False,
					"SDB:="			, False
				],
				[
					"NAME:TPERIO",
					"OverridingDef:="	, True,
					"Value:="		, "Tend+1",
					"NetlistUnits:="	, "s",
					"ShowPin:="		, False,
					"Display:="		, False,
					"Sweep:="		, False,
					"SDB:="			, False
				]
			]
		]
	])
editor.ChangeProperty(
	[
		"NAME:AllTabs",
		[
			"NAME:PassedParameterTab",
			[
				"NAME:PropServers",
				editor.GetCompInstanceFromInstanceName("source2").GetPropServerName()
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:CH_DATA",
					"OverridingDef:="	, True,
					"Value:="		, "$input2"
				]
			]
		],
		[
			"NAME:Quantities",
			[
				"NAME:PropServers",
				editor.GetCompInstanceFromInstanceName("source2").GetPropServerName()
			],
			[
				"NAME:ChangedProps",
				[
					"NAME:PERIO",
					"OverridingDef:="	, True,
					"Value:="		, "0",
					"NetlistUnits:="	, "",
					"ShowPin:="		, False,
					"Display:="		, False,
					"Sweep:="		, False,
					"SDB:="			, False
				],
				[
					"NAME:TPERIO",
					"OverridingDef:="	, True,
					"Value:="		, "Tend+1",
					"NetlistUnits:="	, "s",
					"ShowPin:="		, False,
					"Display:="		, False,
					"Sweep:="		, False,
					"SDB:="			, False
				]
			]
		]
	])

# Add Datapairs component pin so that its location can directly be retrieved #TODO - how to fix this as part of CircuitComponent/pins class
pins = list(source1._oeditor.GetComponentPins(source1.composed_name))
for pin in pins:
    source1.pins.append(CircuitPins(source1, pin, 1))
pins = list(source2._oeditor.GetComponentPins(source2.composed_name))
for pin in pins:
    source2.pins.append(CircuitPins(source2, pin, 1))

# Connect components with wires
#tb.modeler.schematic.create_wire(points=[[22 * G, 29 * G], rom1.pins[0].location])
#tb.modeler.schematic.create_wire(points=[[22 * G, 25 * G], rom1.pins[1].location])
tb.modeler.schematic.create_wire(points=[source1.pins[0].location, rom1.pins[0].location])
tb.modeler.schematic.create_wire(points=[source2.pins[0].location, rom1.pins[1].location])

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

###############################################################################
# Parametrize transient setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parametrize the default transient setup by setting the end time and minimum/maximum time steps.

tb.set_end_time("700s")
tb.set_hmin("0.001s")
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
# the values for the inputs and outputs of the LTI ROM.

variables_postprocessing = []
rom_pins = My_s.lower().split(",")
fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(18, 7))
fig.subplots_adjust(hspace=0.5)

for i in range(0,2):
    variable = 'ROM1.' + rom_pins[i]
    x = tb.post.get_solution_data(variable, "TR", "Time")
    ax[0].plot([el / 1000000000.0 for el in x.intrinsics["Time"]], x.data_real(variable), label=variable) #TODO how to change default time units nanosec to sec ?

ax[0].set_title("ROM inputs")
ax[0].legend(loc="upper left")

for i in range(2, 4):
    variable = 'ROM1.' + rom_pins[i]
    x = tb.post.get_solution_data(variable, "TR", "Time")
    ax[1].plot([el / 1000000000.0 for el in x.intrinsics["Time"]], x.data_real(variable), label=variable)

ax[1].set_title("ROM outputs")
ax[1].legend(loc="upper left")

# Show plot
plt.show()

###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulation is completed, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

# Clean up the downloaded data
shutil.rmtree(source_data_folder)

# Restore earlier desktop configuration and schematic environment
tb.odesktop.SetDesktopConfiguration(current_desktop_config)
tb.odesktop.SetSchematicEnvironment(current_schematic_environment)

tb.release_desktop()
