# # EDB: Pin to Pin project
#
# This example demonstrates the use of the Electronics
# Database (EDB) interface to create a layout using the BOM and
# a configuration file.

# ## Perform required imports
#
# The ``Hfss3dlayout`` class provides an interface to
# the 3D Layout editor in Elecronics Deskop. 
# on version 2023 R2.

import os
import pyaedt
import tempfile

# Download the AEDB file and copy it to a temporary folder.

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
target_aedb = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', 
                                             destination=temp_dir.name)
print("Project folder will be", target_aedb)

# ## Launch EDB
#
# Launch the `pyaedt.Edb` class using EDB 2023 R2. Length units are SI.

edbapp = pyaedt.Edb(target_aedb, edbversion="2023.2")

# ## Import Definitions
#
# The definition file uses the [json](https://www.json.org/json-en.html) to
# map layout part numbers to their corresponding models.
#
# The model may be RLC, Sparameter or a
# [SPICE](https://en.wikipedia.org/wiki/SPICE) model definition.
# Once imported the, definition is applied to the components in the layout.
# In this example the json file is in the ``*.aedb`` folder and has the following format:
# ``` json
# {
#     "SParameterModel": {
#         "GRM32_DC0V_25degC_series": "./GRM32_DC0V_25degC_series.s2p"
#     },
#     "SPICEModel": {
#         "GRM32_DC0V_25degC": "./GRM32_DC0V_25degC.mod"
#     },
#     "Definitions": {
#         "CAPC1005X05N": {
#             "Component_type": "Capacitor",
#             "Model_type": "RLC",
#             "Res": 1,
#             "Ind": 2,
#             "Cap": 3,
#             "Is_parallel": false
#         },
#         "'CAPC3216X180X55ML20T25": {
#             "Component_type": "Capacitor",
#             "Model_type": "SParameterModel",
#             "Model_name": "GRM32_DC0V_25degC_series"
#         },
#         "'CAPC3216X180X20ML20": {
#             "Component_type": "Capacitor",
#             "Model_type": "SPICEModel",
#             "Model_name": "GRM32_DC0V_25degC"
#         }
#     }
# }
# ```
#
# The method ``Edb.components.import_definitions`` imports the componet definitions that map electrical models to the components in the simulaton model.

edbapp.components.import_definition(os.path.join(target_aedb, 
                                                 "1_comp_definition.json"))

# ## Import BOM
#
# The bill of materials (BOM) file provides the list of all components
# by reference designator, part name, component type, and nominal value.
#
# Components that are not contained in the BOM are deactivated in the
# simulation model.
# In this example the csv file was saved in the aedb folder.
#
# ```
# +------------+-----------------------+-----------+------------+
# | RefDes     | Part name             | Type      | Value      |
# +============+=======================+===========+============+
# | C380       | CAPC1005X55X25LL05T10 | Capacitor | 11nF       |
# +------------+-----------------------+-----------+------------+
# ```
#
# Having red the informaton in the BOM and definitions file, electrical models can be
# assigned to all of the components in the simulation model.

edbapp.components.import_bom(os.path.join(target_aedb, "0_bom.csv"),
                                  refdes_col=0,
                                  part_name_col=1,
                                  comp_type_col=2,
                                  value_col=3)

# ## Verify a Component
#
# Component property allows to access all components instances and their property with getters and setters.

comp = edbapp.components["C1"]
comp.model_type, comp.value

# ## Check Component Definition
#
# When an s-parameter model is associated to a component it will be available in nport_comp_definition property.

edbapp.components.nport_comp_definition
edbapp.save_edb()

# ## Configure the Simulation Setup
#
# This step enables the following:
#  - Definition of nets to be included in a cutout region
#  - Cutout details
#  - Components on which to create the ports
#  - Simulation settings
#
# The method ``Edb.new_simulaton_configuration()`` returns an instance 
# of the [``SimulationConfiguration``](https://aedt.docs.pyansys.com/version/stable/EDBAPI/SimulationConfigurationEdb.html) class.

# +
sim_setup = edbapp.new_simulation_configuration()
sim_setup.solver_type = sim_setup.SOLVER_TYPE.SiwaveSYZ
sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.003
sim_setup.batch_solve_settings.do_cutout_subdesign = True
sim_setup.batch_solve_settings.use_pyaedt_cutout = True
sim_setup.ac_settings.max_arc_points = 6
sim_setup.ac_settings.max_num_passes = 5

sim_setup.batch_solve_settings.signal_nets = ['PCIe_Gen4_TX2_CAP_P',
                                              'PCIe_Gen4_TX2_CAP_N',
                                              'PCIe_Gen4_TX2_P',
                                              'PCIe_Gen4_TX2_N']
sim_setup.batch_solve_settings.components = ["U1", "X1"]
sim_setup.batch_solve_settings.power_nets = ["GND", "GND_DP"]
sim_setup.ac_settings.start_freq = "100Hz"
sim_setup.ac_settings.stop_freq = "6GHz"
sim_setup.ac_settings.step_freq = "10MHz"
# -

# ## Implement the Setup
#
# The cutout and all other simulation settings are applied to the simulation model.

sim_setup.export_json(os.path.join(temp_dir.name, "configuration.json"))
edbapp.build_simulation_project(sim_setup)

# ## Display the Cutout
#
# Plot cutout once finished. The model is ready to simulate.

edbapp.nets.plot(None,None)

# ## Save and Close EDB
#
# Edb will be saved and re-opened in Electronics
# Deskopt 3D Layout. The HFSS simulation can then be run.

edbapp.save_edb()
edbapp.close_edb()

# ## Open Electronics Desktop
#
# The EDB is opened in AEDT Hfss3DLayout.
#
# Set ``non_graphical=True`` to run the simulation in non-graphical mode.

h3d = pyaedt.Hfss3dLayout(specified_version="2023.2", 
                          projectname=target_aedb, 
                          non_graphical=False, 
                          new_desktop_session=False)

# ## Analyze
#
# This project is ready to solve. Executing the following cell runs the HFSS simulatoin on the layout.

h3d.analyze()

# ## View Results
#
# S-Parameter data will be loaded at the end of simulation.

solutions = h3d.post.get_solution_data()

# ## Plot Results
#
# Plot S-Parameter data.

solutions.plot(solutions.expressions, "db20")

# ## Save and Close AEDT
#
# Hfss3dLayout is saved and closed.

h3d.save_project()
h3d.release_desktop()

# Clean up the temporary directory. All files and the temporary project
# folder will be deleted in the next step.

temp_dir.cleanup()
