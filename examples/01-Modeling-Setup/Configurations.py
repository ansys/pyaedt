"""
General: Configuration Files
----------------------------
This example shows how you can use PyAEDT to export config files and reuse to import in a new project.
Configuration file is actually supported by the following applications:
* Hfss
* Q2d and Q3d
* Maxwell
* Icepak
* Mechanical

The sections covered are:

* Variables
* Mesh Operations (except Icepak)
* Setup and Optimetrics
* Material Properties
* Object Properties
* Boundaries and Excitations

When a boundary is attached to a face the tool will try to match it with a
FaceByPosition on the same object name on the target design.
If, for any reason, that face position has changed or object name in the target design has changed,
the boundary will fail to apply.
"""

###############################################################################
# Perform Required Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# This example performs required imports from PyAEDT and connects to AEDT.

import os
import tempfile
import shutil
from pyaedt import Icepak
from pyaedt import examples
from pyaedt import generate_unique_name


##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Open Project
# ~~~~~~~~~~~~
# Download Project, opens it and save to TEMP Folder.

project_full_name = examples.download_icepak()

tmpfold = tempfile.gettempdir()


temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
project_temp_name = os.path.join(temp_folder, "Graphic_Card.aedt")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
shutil.copy2(project_full_name, project_temp_name)

ipk = Icepak(project_temp_name, specified_version="2022.2", new_desktop_session=True, non_graphical=non_graphical)
ipk.save_project(os.path.join(temp_folder, "Graphics_card.aedt"))
ipk.autosave_disable()

###############################################################################
# Create Source Blocks
# ~~~~~~~~~~~~~~~~~~~~
# Create Source block on CPU and MEMORIES

ipk.create_source_block("CPU", "25W")
ipk.create_source_block(["MEMORY1", "MEMORY1_1"], "5W")

###############################################################################
# Assign Boundaries
# ~~~~~~~~~~~~~~~~~
# Assign Opening and Grille

region = ipk.modeler["Region"]
ipk.assign_openings(air_faces=region.bottom_face_x.id)
ipk.assign_grille(air_faces=region.top_face_x.id, free_area_ratio=0.8)

###############################################################################
# Setup
# ~~~~~
# Create Setup

setup1 = ipk.create_setup()
setup1.props["Flow Regime"] = "Turbulent"
setup1.props["Convergence Criteria - Max Iterations"] = 5
setup1.props["Linear Solver Type - Pressure"] = "flex"
setup1.props["Linear Solver Type - Temperature"] = "flex"
ipk.save_project(r"C:\temp\Graphic_card.aedt")

###############################################################################
# Export the Step File
# ~~~~~~~~~~~~~~~~~~~~
# This command export the current project to step file.

filename = ipk.design_name
file_path = os.path.join(ipk.working_directory, filename + ".step")
ipk.export_3d_model(filename, ipk.working_directory, ".step", [], [])

###############################################################################
# Export Configuration Files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example defines how to export configuration files.
# Optionally user can disable export /import sections.

conf_file = ipk.configurations.export_config()
ipk.close_project()

###############################################################################
# Create a new Project
# ~~~~~~~~~~~~~~~~~~~~
# This section we create a new Icepak project and iport the step.

app = Icepak(projectname="new_proj_Ipk")
app.modeler.import_3d_cad(file_path)

###############################################################################
# Import and apply the configuration file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User can apply all or part of the json imported using options in configurations object.

out = app.configurations.import_config(conf_file)
app.configurations.results.global_import_success


###############################################################################
# Close the project
# ~~~~~~~~~~~~~~~~~

if os.name != "posix":
    app.release_desktop()
