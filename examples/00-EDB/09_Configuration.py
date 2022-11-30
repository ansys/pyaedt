"""
EDB: fully configurable project
-------------------------------
This example shows how you can use create a project using BOM file and configuration files,
run anlasyis and get results.

"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Peform required imports. Importing the ``Hfss3dlayout`` object initializes it
# on version 2022 R2.

import os

from pyaedt import generate_unique_folder_name,examples, Edb, Hfss3dLayout
from pyaedt.generic.constants import SolverType
from pyaedt.edb_core.edb_data.simulation_configuration import SimulationConfiguration

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``True``.

non_graphical = True

###############################################################################
# Download file
# ~~~~~~~~~~~~~
# Download the AEDB file and copy it in the temporary folder.


project_path = generate_unique_folder_name()
target_aedb = examples.download_file('edb/Galileo.aedb',destination=project_path)
print("Project folder will be", target_aedb)

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyaedt.Edb` class, using EDB 2022 R2 and SI units.

edbapp = Edb(target_aedb, edbversion="2022.2")
###############################################################################
# Import Definitions
# ~~~~~~~~~~~~~~~~~~
# A definitions file is a json containing, for each part name the model associated.
# Model can be RLC, Sparameter or Spice.
# Once imported the definition is applied to the board.
# Json file is stored for convenience in aedb folder.

edbapp.core_components.import_definition(os.path.join(target_aedb, "1_comp_definition.json"))

###############################################################################
# Import BOM
# ~~~~~~~~~~
# This steps import a bom csv file containg, reference designator,
# part name, component type and default value.
# Components not in BOM will be deactivated.
# Csv file is store for convenience in aedb folder.

edbapp.core_components.import_bom(os.path.join(target_aedb,"0_bom.csv"),
                                  refdes_col=0,
                                  part_name_col=1,
                                  comp_type_col=2,
                                  value_col=3)



###############################################################################
# Check Component Values
# ~~~~~~~~~~~~~~~~~~~~~~

comp = edbapp.core_components.components["C3B14"]
comp.model_type, comp.value

###############################################################################
# Check Component Values
# ~~~~~~~~~~~~~~~~~~~~~~
comp2 = edbapp.core_components.components["C3A3"]
comp2.model_type, comp2.value

###############################################################################
# Check Component Definition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

edbapp.core_components.nport_comp_definition

###############################################################################
# Save Edb
# ~~~~~~~~
edbapp.save_edb()

###############################################################################
# Configure Setup
# ~~~~~~~~~~~~~~~
# This step allows to define the project. It includes:
#  - Definition of nets to be included into the cutout
#  - Cutout details
#  - Components on which to create the ports
#  - Simulation settings

sim_setup = edbapp.new_simulation_configuration()
sim_setup.solver_type = SolverType.SiwaveSYZ
sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.01
sim_setup.batch_solve_settings.do_cutout_subdesign = True
sim_setup.batch_solve_settings.signal_nets = ["PCIE0_RX0_P", "PCIE0_RX0_N", "PCIE0_TX0_P_C", "PCIE0_TX0_N_C",
                                              "PCIE0_TX0_P", "PCIE0_TX0_N"]
sim_setup.batch_solve_settings.components = ["U2A5", "J2L1"]
sim_setup.batch_solve_settings.power_nets = ["GND"]
sim_setup.ac_settings.start_freq = "100Hz"
sim_setup.ac_settings.stop_freq = "6GHz"
sim_setup.ac_settings.step_freq = "10MHz"

###############################################################################
# Run Setup
# ~~~~~~~~~
# This step allows to create the cutout and apply all settings.

sim_setup.export_json(os.path.join(project_path, "configuration.json"))
edbapp.build_simulation_project(sim_setup)

###############################################################################
# Plot Cutout
# ~~~~~~~~~~~
# Plot cutout once finished.

edbapp.core_nets.plot(None,None)

###############################################################################
# Save and Close EDB
# ~~~~~~~~~~~~~~~~~~
# Edb will be saved and closed in order to be opened by Hfss 3D Layout and solved.

edbapp.save_edb()
edbapp.close_edb()

###############################################################################
# Open Aedt
# ~~~~~~~~~
# Project folder aedb will be opened in AEDT Hfss3DLayout and loaded.
h3d = Hfss3dLayout(specified_version="2022.2", projectname=target_aedb, non_graphical=non_graphical)

###############################################################################
# Analyze
# ~~~~~~~
# Project will be solved.
h3d.analyze_nominal()

###############################################################################
# Get Results
# ~~~~~~~~~~~
# S Parameter data will be loaded at the end of simulation.
solutions = h3d.post.get_solution_data()

###############################################################################
# Plot Results
# ~~~~~~~~~~~~
# Plot S Parameter data.
solutions.plot(solutions.expressions, "db20")

###############################################################################
# Save and Close AEDT
# ~~~~~~~~~~~~~~~~~~~
# Hfss3dLayout is saved and closed.
h3d.save_project()
h3d.release_desktop()
