"""
Maxwell 3d: Bath Plate
----------------------
This example uses PyAEDT to setup the TEAM3 problem.
This is solved using the Maxwell 3D Eddy Current solver
"""

import os

from pyaedt import Maxwell3d

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

##################################################################################
# Launch AEDT and Maxwell 3D.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an instance of the Maxwell3d class named M3D
# The project and design names along with solver and version type can then be set.

Project_Name = "COMPUMAG"
Design_Name = "TEAM 3 Bath Plate"
Solver = "EddyCurrent"
DesktopVersion = "2022.1"

M3D = Maxwell3d(
    projectname=Project_Name,
    designname=Design_Name,
    solution_type=Solver,
    specified_version=DesktopVersion,
    non_graphical=non_graphical,
    new_desktop_session=True,
)
uom = M3D.modeler.model_units = "mm"
modeler = M3D.modeler

###############################################################################
# Add the variable Coil Position, it will later be used to adjust position of the coil
Coil_Position = -20
M3D["Coil_Position"] = str(Coil_Position) + uom  # Creates a design variable in Maxwell

################################################################################
# Create TEAM3 aluminium material for the ladder plate
mat = M3D.materials.add_material("team3_aluminium")
mat.conductivity = 32780000

###############################################################################
# Draw Geometry and Assign Mesh Operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Draw a background region, it will take default Air properties
M3D.modeler.create_air_region(x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=100)

################################################################################
# Draw ladder plate and assign 'team3_aluminium'
M3D.modeler.create_box([-30, -55, 0], [60, 110, -6.35], name="LadderPlate", matname="team3_aluminium")
M3D.modeler.create_box([-20, -35, 0], [40, 30, -6.35], name="CutoutTool1")
M3D.modeler.create_box([-20, 5, 0], [40, 30, -6.35], name="CutoutTool2")
M3D.modeler.subtract("LadderPlate", ["CutoutTool1", "CutoutTool2"], keepOriginals=False)

################################################################################
# Add a mesh refinement to the ladder plate
M3D.mesh.assign_length_mesh("LadderPlate", maxlength=3, maxel=None, meshop_name="Ladder_Mesh")

################################################################################
# Draw Search Coil and Assign a Stranded Current Excitation
# The 'stranded' type forces current density to be constant in the coil
M3D.modeler.create_cylinder(
    cs_axis="Z", position=[0, "Coil_Position", 15], radius=40, height=20, name="SearchCoil", matname="copper"
)
M3D.modeler.create_cylinder(
    cs_axis="Z", position=[0, "Coil_Position", 15], radius=20, height=20, name="Bore", matname="copper"
)
M3D.modeler.subtract("SearchCoil", "Bore", keepOriginals=False)
M3D.modeler.section("SearchCoil", "YZ")
M3D.modeler.separate_bodies("SearchCoil_Section1")
M3D.modeler.delete("SearchCoil_Section1_Separate1")
M3D.assign_current(["SearchCoil_Section1"], amplitude=1260, solid=False, name="SearchCoil_Excitation")

################################################################################
# Draw a line we will later use it to plot Bz on, (z-component of Flux Density)
# A small diameter cylinder is also added to refine mesh locally around the line.
Line_Points = [["0mm", "-55mm", "0.5mm"], ["0mm", "55mm", "0.5mm"]]
P1 = modeler.create_polyline(Line_Points, name="Line_AB")
P2 = modeler.create_polyline(Line_Points, name="Line_AB_MeshRefinement")
P2.set_crosssection_properties(type="Circle", width="0.5mm")


###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

M3D.plot(show=False, export_path=os.path.join(M3D.working_directory, "Image.jpg"), plot_air_objects=False)


###############################################################################
# Setup Maxwell 3D Model
# ~~~~~~~~~~~~~~~~~~~~~~
# Add analysis setup with frequency points at 50Hz and 200Hz
Setup = M3D.create_setup(setupname="Setup1")
Setup.props["Frequency"] = "200Hz"
Setup.props["HasSweepSetup"] = True
Setup.add_eddy_current_sweep("LinearStep", 50, 200, 150, clear=True)


################################################################################
# Adjust Eddy Effects for LadderPlate and SearchCoil
# NB, Eddy effect setting is ignored for stranded conductor type used in Search Coil
M3D.eddy_effects_on(["LadderPlate"], activate_eddy_effects=True, activate_displacement_current=True)
M3D.eddy_effects_on(["SearchCoil"], activate_eddy_effects=False, activate_displacement_current=True)

################################################################################
# Add a linear parametric sweep for the two coil positions
sweepname = "CoilSweep"
param = M3D.parametrics.add("Coil_Position", -20, 0, 20, "LinearStep", parametricname=sweepname)
param.props["ProdOptiSetupDataV2"]["SaveFields"] = True
param.props["ProdOptiSetupDataV2"]["CopyMesh"] = False
param.props["ProdOptiSetupDataV2"]["SolveWithCopiedMeshOnly"] = True

# Solve the model, we solve the parametric sweep directly so results of all variations are available.
M3D.analyze_setup(sweepname)

###############################################################################
# Postprocessing Field Plots and Graphs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

################################################################################
# Use fields calculator to create expression for Bz
Fields = M3D.odesign.GetModule("FieldsReporter")
Fields.EnterQty("B")
Fields.CalcOp("ScalarZ")
Fields.EnterScalar(1000)
Fields.CalcOp("*")
Fields.CalcOp("Smooth")
Fields.AddNamedExpression("Bz", "Fields")

###############################################################################
# Plot mag(Bz) as a function of frequency for both coil positions
variations = {"Distance": ["All"], "Freq": ["All"], "Phase": ["0deg"], "Coil_Position": ["-20mm"]}
M3D.post.create_report(
    expressions="mag(Bz)",
    report_category="Fields",
    context="Line_AB",
    variations=variations,
    primary_sweep_variable="Distance",
    plotname="mag(Bz) Along 'Line_AB' Offset Coil",
)

variations = {"Distance": ["All"], "Freq": ["All"], "Phase": ["0deg"], "Coil_Position": ["0mm"]}
M3D.post.create_report(
    expressions="mag(Bz)",
    report_category="Fields",
    context="Line_AB",
    variations=variations,
    primary_sweep_variable="Distance",
    plotname="mag(Bz) Along 'Line_AB' Coil",
)


###############################################################################
# Postprocessing
# --------------
# The same report can be obtained outside electronic desktop with the
# following commands.
variations = {"Distance": ["All"], "Freq": ["All"], "Phase": ["0deg"], "Coil_Position": ["All"]}

solutions = M3D.post.get_solution_data(
    expressions="mag(Bz)",
    report_category="Fields",
    context="Line_AB",
    variations=variations,
    primary_sweep_variable="Distance",
)

###############################################################################
# Postprocessing
# --------------
# User can setup a sweep value and plot the solution.

solutions.active_variation["Coil_Position"] = -0.02
solutions.plot()

###############################################################################
# Postprocessing
# --------------
# User can change a sweep value and plot again.

solutions.active_variation["Coil_Position"] = 0
solutions.plot()


###############################################################################
# Create a plot Mag_J, the induced current density on the surface of the ladder plate
surflist = modeler.get_object_faces("LadderPlate")
intrinsic_dict = {"Freq": "50Hz", "Phase": "0deg"}
M3D.post.create_fieldplot_surface(surflist, "Mag_J", intrinsincDict=intrinsic_dict, plot_name="Mag_J")

###############################################################################
# The electronics desktop is released from the script engine, we leave the desktop and project open.
M3D.release_desktop(True, True)
