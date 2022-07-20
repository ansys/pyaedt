"""
Icepak: graphic card thermal analysis
-------------------------------------
This example shows how you can use PyAEDT to create a graphic card setup in Icepak and postprocess results.
The example file is an Icepak project with a model that is already created and has materials assigned.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import tempfile
import shutil
from pyaedt import examples, generate_unique_name
from pyaedt import Icepak

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Download and open project
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the project, open it, and save it to the temporary folder.

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
# Plot model
# ~~~~~~~~~~
# Plot the model.

ipk.plot(show=False, export_path=os.path.join(temp_folder, "Graphics_card.jpg"), plot_air_objects=False)

###############################################################################
# Create source blocks
# ~~~~~~~~~~~~~~~~~~~~
# Create source blocks on the CPU and memories.

ipk.create_source_block("CPU", "25W")
ipk.create_source_block(["MEMORY1", "MEMORY1_1"], "5W")

###############################################################################
# Assign openings and grille
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assign openings and a grille.

region = ipk.modeler["Region"]
ipk.assign_openings(air_faces=region.bottom_face_x.id)
ipk.assign_grille(air_faces=region.top_face_x.id, free_area_ratio=0.8)

###############################################################################
# Assign mesh regions
# ~~~~~~~~~~~~~~~~~~~
# Assign a mesh region to the heat sink and CPU.

mesh_region = ipk.mesh.assign_mesh_region(objectlist=["HEAT_SINK", "CPU"])
mesh_region.UserSpecifiedSettings = True
mesh_region.MaxElementSizeX = "3.35mm"
mesh_region.MaxElementSizeY = "1.75mm"
mesh_region.MaxElementSizeZ = "2.65mm"
mesh_region.MaxLevels = "2"
mesh_region.update()

###############################################################################
# Assign point monitor
# ~~~~~~~~~~~~~~~~~~~~
# Assign a point monitor and set it up.

ipk.assign_point_monitor(point_position=["-35mm", "3.6mm", "-86mm"], monitor_name="TemperatureMonitor1")
ipk.assign_point_monitor(point_position=["80mm", "14.243mm", "-55mm"], monitor_type="Speed")
setup1 = ipk.create_setup()
setup1.props["Flow Regime"] = "Turbulent"
setup1.props["Convergence Criteria - Max Iterations"] = 5
setup1.props["Linear Solver Type - Pressure"] = "flex"
setup1.props["Linear Solver Type - Temperature"] = "flex"
ipk.save_project(r"C:\temp\Graphic_card.aedt")

###############################################################################
# Solve project and postprocess
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve the project and plot temperatures.

quantity_name = "SurfTemperature"
surflist = [i.id for i in ipk.modeler["CPU"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1"].faces]
surflist += [i.id for i in ipk.modeler["MEMORY1_1"].faces]
surflist += [i.id for i in ipk.modeler["ALPHA_MAIN_PCB"].faces]

plot5 = ipk.post.create_fieldplot_surface(surflist, "SurfTemperature")


ipk.analyze_nominal()

###############################################################################
# Release AEDT
# ~~~~~~~~~~~~
# Release AEDT.

ipk.release_desktop(True, True)
