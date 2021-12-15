"""
Maxwell 3D TEAM3 Bath Plate
---------------------------
This example uses PyAEDT to setup the TEAM3 problem set by COMPUMAG.
This is solved using the Maxwell 3D Eddy Current solver
"""

# sphinx_gallery_thumbnail_path = 'Resources/Maxwell3DTeam3.png'

from pyaedt import Maxwell3d

##################################################################################
# Launch AEDT and Maxwell 3D.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an instance of the Maxwell3d class named M3D
# The project and design names along with solver and version type can then be set.

Project_Name = "COMPUMAG"
Design_Name = "TEAM 3 Bath Plate"
Solver = "EddyCurrent"
DesktopVersion = "2021.2"
NonGraphical = False

M3D = Maxwell3d(
    projectname=Project_Name,
    designname=Design_Name,
    solution_type=Solver,
    specified_version=DesktopVersion,
    non_graphical=NonGraphical,
)
uom = M3D.modeler.model_units = "mm"
primitives = M3D.modeler.primitives

###############################################################################
# Add the variable Coil Position, it will later be used to adjust position of the coil
Coil_Position = -20
M3D["Coil_Position"] = str(Coil_Position) + uom  # Creates a design variable in Maxwell

################################################################################
# Create TEAM3 aluminium material for the ladder plate
mat = M3D.materials.add_material("team3_aluminium")
mat.update()
mat.conductivity = 32780000

###############################################################################
# Draw Geometry and Assign Mesh Operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Draw a background region, it will take default Air properties
M3D.modeler.create_air_region(x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=100)

################################################################################
# Draw ladder plate and assign 'team3_aluminium'
M3D.modeler.primitives.create_box([-30, -55, 0], [60, 110, -6.35], name="LadderPlate", matname="team3_aluminium")
M3D.modeler.primitives.create_box([-20, -35, 0], [40, 30, -6.35], name="CutoutTool1")
M3D.modeler.primitives.create_box([-20, 5, 0], [40, 30, -6.35], name="CutoutTool2")
M3D.modeler.subtract("LadderPlate", ["CutoutTool1", "CutoutTool2"], keepOriginals=False)

################################################################################
# Add a mesh refinement to the ladder plate
M3D.mesh.assign_length_mesh("LadderPlate", maxlength=3, maxel=None, meshop_name="Ladder_Mesh")

################################################################################
# Draw Search Coil and Assign a Stranded Current Excitation
# The 'stranded' type forces current density to be constant in the coil
M3D.modeler.primitives.create_cylinder(
    cs_axis="Z", position=[0, "Coil_Position", 15], radius=40, height=20, name="SearchCoil", matname="copper"
)
M3D.modeler.primitives.create_cylinder(
    cs_axis="Z", position=[0, "Coil_Position", 15], radius=20, height=20, name="Bore", matname="copper"
)
M3D.modeler.subtract("SearchCoil", "Bore", keepOriginals=False)
M3D.modeler.section("SearchCoil", "YZ")
M3D.modeler.separate_bodies("SearchCoil_Section1")
M3D.modeler.primitives.delete("SearchCoil_Section1_Separate1")
M3D.assign_current(["SearchCoil_Section1"], amplitude=1260, solid=False, name="SearchCoil_Excitation")

################################################################################
# Draw a line we will later use it to plot Bz on, (z-component of Flux Density)
# A small diameter cylinder is also added to refine mesh locally around the line.
Line_Points = [["0mm", "-55mm", "0.5mm"], ["0mm", "55mm", "0.5mm"]]
P1 = primitives.create_polyline(Line_Points, name="Line_AB")
P2 = primitives.create_polyline(Line_Points, name="Line_AB_MeshRefinement")
P2.set_crosssection_properties(type="Circle", width="0.5mm")

###############################################################################
# Setup Maxwell 3D Model
# ~~~~~~~~~~~~~~~~~~~~~~
# Add analysis setup with frequency points at 50Hz and 200Hz
Setup = M3D.create_setup(setupname="Setup1")
Setup.props["Frequency"] = "200Hz"
Setup.props["HasSweepSetup"] = True
Setup.props["StartValue"] = "50Hz"
Setup.props["StopValue"] = "200Hz"
Setup.props["StepSize"] = "150Hz"
Setup.update()

################################################################################
# Adjust Eddy Effects for LadderPlate and SearchCoil
# NB, Eddy effect setting is ignored for stranded conductor type used in Search Coil
M3D.eddy_effects_on(["LadderPlate"], activate=True)
M3D.eddy_effects_on(["SearchCoil"], activate=False)

################################################################################
# Add a linear parametric sweep for the two coil positions
sweepname = "CoilSweep"
param = M3D.opti_parametric.add_parametric_setup("Coil_Position", "LIN -20mm 0mm 20mm", parametricname=sweepname)
param.props["ProdOptiSetupDataV2"]["SaveFields"] = True
param.props["ProdOptiSetupDataV2"]["CopyMesh"] = False
param.props["ProdOptiSetupDataV2"]["SolveWithCopiedMeshOnly"] = True
param.update()

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
Plot = M3D.odesign.GetModule("ReportSetup")
Plot.CreateReport(
    "mag(Bz) Along 'Line_AB' Offset Coil",
    "Fields",
    "Rectangular Plot",
    "Setup1 : LastAdaptive",
    ["Context:=", "Line_AB", "PointCount:=", 1001],
    ["Distance:=", ["All"], "Freq:=", ["All"], "Phase:=", ["0deg"], "Coil_Position:=", ["-20mm"]],
    ["X Component:=", "Distance-60mm", "Y Component:=", ["mag(Bz)"]],
)

Plot.CreateReport(
    "mag(Bz) Along 'Line_AB' Centred Coil",
    "Fields",
    "Rectangular Plot",
    "Setup1 : LastAdaptive",
    ["Context:=", "Line_AB", "PointCount:=", 1001],
    ["Distance:=", ["All"], "Freq:=", ["All"], "Phase:=", ["0deg"], "Coil_Position:=", ["0mm"]],
    ["X Component:=", "Distance-60mm", "Y Component:=", ["mag(Bz)"]],
)

###############################################################################
# Create a plot Mag_J, the induced current density on the surface of the ladder plate
surflist = primitives.get_object_faces("LadderPlate")
intrinsic_dict = {"Freq": "50Hz", "Phase": "0deg"}
M3D.post.create_fieldplot_surface(surflist, "Mag_J", intrinsincDict=intrinsic_dict, plot_name="Mag_J")

###############################################################################
# The electronics desktop is released from the script engine, we leave the desktop and project open.
M3D.release_desktop(False, False)
