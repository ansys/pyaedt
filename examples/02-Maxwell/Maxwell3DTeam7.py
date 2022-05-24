"""
Maxwell 3d: Symmetrical Conductor with a Hole
---------------------------------------------
This example uses PyAEDT to setup the TEAM 7 problem.
This is solved using the Maxwell 3D Eddy Current solver.
"""
from pyaedt import Maxwell3d
import numpy as np
import csv
import os

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###########################################################################################
# Launch AEDT and Maxwell 3D.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an instance of the Maxwell3d class named M3D
# The project and design names along with solver and version type can then be set.

Project_Name = "COMPUMAG"
Design_Name = "TEAM 7 Asymmetric Conductor"
Solver = "EddyCurrent"
DesktopVersion = "2022.1"

M3D = Maxwell3d(
    projectname=Project_Name, designname=Design_Name, solution_type=Solver, specified_version=DesktopVersion, non_graphical=non_graphical
)
M3D.modeler.model_units = "mm"
modeler = M3D.modeler
Plot = M3D.odesign.GetModule("ReportSetup")


###########################################################################################
# Setup Maxwell 3D Model
# ~~~~~~~~~~~~~~~~~~~~~~
# An analysis setup is added with frequency points at DC, 50Hz and 200Hz
# Otherwise the default PyAEDT setup values will be taken
# A low frequency value is used to approximate a DC field in the EddyCurrent Solver.
# Second order shape functions improve the smoothness of the induced currents in the plate.

dc_freq = 0.1
stop_freq = 50

Setup = M3D.create_setup(setupname="Setup1")
Setup.props["Frequency"] = "200Hz"
Setup.props["HasSweepSetup"] = True
Setup.add_eddy_current_sweep("LinearStep", dc_freq, stop_freq, stop_freq - dc_freq, clear=True)
Setup.props["UseHighOrderShapeFunc"] = True
Setup.props["PercentError"] = 0.4

###########################################################################################
# Coil Dimensions
# ~~~~~~~~~~~~~~~
# Dimensions are entered as shown on TEAM7 drawing of coil.
coil_external = 150 + 25 + 25
coil_internal = 150
coil_r1 = 25
coil_r2 = 50
coil_thk = coil_r2 - coil_r1
coil_height = 100
coil_centre = [294 - 25 - 150 / 2, 25 + 150 / 2, 19 + 30 + 100 / 2]

# Expressions are used to construct three dimensions needed to describe mid points of coil.
dim1 = coil_internal / 2 + (coil_external - coil_internal) / 4
dim2 = coil_internal / 2 - coil_r1
dim3 = dim2 + np.sqrt(((coil_r1 + (coil_r2 - coil_r1) / 2) ** 2) / 2)

# Coordinates are used to draw a polyline along which coil cross section will be swept.
P1 = [dim1, -dim2, 0]
P2 = [dim1, dim2, 0]
P3 = [dim3, dim3, 0]
P4 = [dim2, dim1, 0]

###########################################################################################
# Draw Coil and Plate Geometry and Material Properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a Coordinate System to be used for positioning the coil
M3D.modeler.create_coordinate_system(origin=coil_centre, mode="view", view="XY", name="Coil_CS")

# One quarter of the Coil is modelled by sweeping a 2D sheet along a polyline.
# Duplicate and Unite commands then create the full coil.
test = M3D.modeler.create_polyline(position_list=[P1, P2, P3, P4], segment_type=["Line", "Arc"], name="Coil")
test.set_crosssection_properties(type="Rectangle", width=coil_thk, height=coil_height)
M3D.modeler.duplicate_around_axis(
    "Coil", cs_axis="Global", angle=90, nclones=4, create_new_objects=True, is_3d_comp=False
)
M3D.modeler.unite("Coil,Coil_1,Coil_2")
M3D.modeler.unite("Coil,Coil_3")
M3D.modeler.fit_all()

# Maxwell internal library Copper is assigned to the coil and we allow solution inside the Coil
M3D.assign_material("Coil", "Copper")
M3D.solve_inside("Coil")

# Create Terminal for Coil from a cross section that is then split and one half deleted
M3D.modeler.section("Coil", "YZ")
M3D.modeler.separate_bodies("Coil_Section1")
M3D.modeler.delete("Coil_Section1_Separate1")

# Add a design variable in Maxwell for the coil Excitation, NB Units here are AmpereTurns
Coil_Excitation = 2742
M3D["Coil_Excitation"] = str(Coil_Excitation) + "A"
M3D.assign_current("Coil_Section1", amplitude="Coil_Excitation", solid=False)
M3D.modeler.set_working_coordinate_system("Global")

# Add a new material with Team 7 properties for Aluminium
mat = M3D.materials.add_material("team7_aluminium")
mat.conductivity = 3.526e7

# Model the Aluminium plate with a hole in by subtracting two rectangular cuboids.
plate = M3D.modeler.create_box([0, 0, 0], [294, 294, 19], name="Plate", matname="team7_aluminium")
M3D.modeler.fit_all()
hole = M3D.modeler.create_box([18, 18, 0], [108, 108, 19], name="Hole")
M3D.modeler.subtract("Plate", ["Hole"], keepOriginals=False)

# Draw a background region, it will take default Air properties
M3D.modeler.create_air_region(x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=100)

################################################################################
# Adjust Eddy Effects for Plate and Coil
# Turn off displacement currents for all parts
# NB, Eddy effect setting is regardless ignored for stranded conductor type used in Coil

M3D.eddy_effects_on("Plate")
M3D.eddy_effects_on(["Coil", "Region", "Line_A1_B1mesh", "Line_A2_B2mesh"],
                    activate_eddy_effects=False,
                    activate_displacement_current=False)

################################################################################
# Use Fields Calculator to create an expression for Z Component of B in Gauss
Fields = M3D.odesign.GetModule("FieldsReporter")
Fields.EnterQty("B")
Fields.CalcOp("ScalarZ")
Fields.EnterScalarFunc("Phase")
Fields.CalcOp("AtPhase")
Fields.EnterScalar(10000)
Fields.CalcOp("*")
Fields.CalcOp("Smooth")
Fields.AddNamedExpression("Bz", "Fields")

################################################################################
# Draw two lines along which we will plot Bz
# A small cylinder is also added to refine mesh locally around each line.
lines = ["Line_A1_B1", "Line_A2_B2"]
mesh_diameter = "2mm"

line_points_1 = [["0mm", "72mm", "34mm"], ["288mm", "72mm", "34mm"]]
polyline = modeler.create_polyline(line_points_1, name=lines[0])
L1Mesh = modeler.create_polyline(line_points_1, name=lines[0] + "mesh")
L1Mesh.set_crosssection_properties(type="Circle", width=mesh_diameter)

line_points_2 = [["0mm", "144mm", "34mm"], ["288mm", "144mm", "34mm"]]
polyline2 = modeler.create_polyline(line_points_2, name=lines[1])
polyline2_mesh = modeler.create_polyline(line_points_2, name=lines[1] + "mesh")
polyline2_mesh.set_crosssection_properties(type="Circle", width=mesh_diameter)

###############################################################################
# Plot the Model
# ~~~~~~~~~~~~~~
M3D.plot(show=False, export_path=os.path.join(M3D.working_directory, "Image.jpg"), plot_air_objects=False)


################################################################################
# Published measurement results are included with this script via the list below.
# Test results are then used to create text files for import into rectangular plot and overlay simulation results.

project_dir = M3D.working_directory
dataset = [
    "Bz A1_B1 000 0",
    "Bz A1_B1 050 0",
    "Bz A1_B1 050 90",
    "Bz A1_B1 200 0",
    "Bz A1_B1 200 90",
    "Bz A2_B2 050 0",
    "Bz A2_B2 050 90",
    "Bz A2_B2 200 0",
    "Bz A2_B2 200 90",
]
header = ["Distance [mm]", "Bz [Tesla]"]

line_length = [0, 18, 36, 54, 72, 90, 108, 126, 144, 162, 180, 198, 216, 234, 252, 270, 288]
data = [
    [
        -6.667,
        -7.764,
        -8.707,
        -8.812,
        -5.870,
        8.713,
        50.40,
        88.47,
        100.9,
        104.0,
        104.8,
        104.9,
        104.6,
        103.1,
        97.32,
        75.19,
        29.04,
    ],
    [
        4.90,
        -17.88,
        -22.13,
        -20.19,
        -15.67,
        0.36,
        43.64,
        78.11,
        71.55,
        60.44,
        53.91,
        52.62,
        53.81,
        56.91,
        59.24,
        52.78,
        27.61,
    ],
    [-1.16, 2.84, 4.15, 4.00, 3.07, 2.31, 1.89, 4.97, 12.61, 14.15, 13.04, 12.40, 12.05, 12.27, 12.66, 9.96, 2.36],
    [
        -3.63,
        -18.46,
        -23.62,
        -21.59,
        -16.09,
        0.23,
        44.35,
        75.53,
        63.42,
        53.20,
        48.66,
        47.31,
        48.31,
        51.26,
        53.61,
        46.11,
        24.96,
    ],
    [-1.38, 1.20, 2.15, 1.63, 1.10, 0.27, -2.28, -1.40, 4.17, 3.94, 4.86, 4.09, 3.69, 4.60, 3.48, 4.10, 0.98],
    [
        -1.83,
        -8.50,
        -13.60,
        -15.21,
        -14.48,
        -5.62,
        28.77,
        60.34,
        61.84,
        56.64,
        53.40,
        52.36,
        53.93,
        56.82,
        59.48,
        52.08,
        26.56,
    ],
    [-1.63, -0.60, -0.43, 0.11, 1.26, 3.40, 6.53, 10.25, 11.83, 11.83, 11.01, 10.58, 10.80, 10.54, 10.62, 9.03, 1.79],
    [
        -0.86,
        -7.00,
        -11.58,
        -13.36,
        -13.77,
        -6.74,
        24.63,
        53.19,
        54.89,
        50.72,
        48.03,
        47.13,
        48.25,
        51.35,
        53.35,
        45.37,
        24.01,
    ],
    [-1.35, -0.71, -0.81, -0.67, 0.15, 1.39, 2.67, 3.00, 4.01, 3.80, 4.00, 3.02, 2.20, 2.78, 1.58, 1.37, 0.93],
]

# Dataset detail is used to encode test parameters in the text files.
# For example 'Bz A1_B1 050 0' is the z component of Flux Density, B along line A1_B1 at 50Hz and 0deg
# These text files are created and saved in the default project_dir
print("project_dir", project_dir)
dataset_range = range(int(0), len(dataset), int(1))
line_length_range = range(int(0), len(line_length), int(1))
dataset_list = []

for item in dataset_range:
    dataset_list.clear()
    for jtem in line_length_range:
        dataset_list.insert(jtem, data[item][jtem])
        ziplist = zip(line_length, dataset_list)
    with open(project_dir + "\\" + str(dataset[item]) + ".csv", "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(header)
        writer.writerows(ziplist)

# Create rectangular plots and use text file encoding to control formatting of the rectangular plots
# DC plot is created separately, it needs a different frequency and phase to the other plots.
for item in dataset_range:
    if item % 2 == 0:
        plotname = dataset[item][0:3] + "Along the Line" + dataset[item][2:9] + ", " + dataset[item][9:12] + "Hz"
        if dataset[item][9:12] == "000":
            variations = {
                "Distance": ["All"],
                "Freq": [str(dc_freq) + "Hz"],
                "Phase": ["0deg"],
                "Coil_Excitation": ["All"],
            }
            M3D.post.create_report(
                plotname=plotname,
                report_category="Fields",
                context="Line_" + dataset[item][3:8],
                primary_sweep_variable="Distance",
                variations=variations,
                expressions=dataset[item][0:2],
            )
        else:
            variations = {
                "Distance": ["All"],
                "Freq": [dataset[item][9:12] + "Hz"],
                "Phase": ["0deg", "90deg"],
                "Coil_Excitation": ["All"],
            }
            M3D.post.create_report(
                plotname=plotname,
                report_category="Fields",
                context="Line_" + dataset[item][3:8],
                primary_sweep_variable="Distance",
                variations=variations,
                expressions=dataset[item][0:2],
            )

        # Import test data into the correct plot and overlay it with simulation results.
        if item == 0:
            Plot.ImportIntoReport(plotname, os.path.join(project_dir, str(dataset[item]) + ".csv"))
        else:
            Plot.ImportIntoReport(plotname, project_dir + "\\" + str(dataset[item - 1]) + ".csv")
            Plot.ImportIntoReport(plotname, project_dir + "\\" + str(dataset[item]) + ".csv")

###################################################################################################
# Create two plots of Mag_J and Mag_B, the induced current and flux density on surface of the plate
surflist = modeler.get_object_faces("Plate")
intrinsic_dict = {"Freq": "200Hz", "Phase": "0deg"}
M3D.post.create_fieldplot_surface(surflist, "Mag_J", intrinsincDict=intrinsic_dict, plot_name="Mag_J")
M3D.post.create_fieldplot_surface(surflist, "Mag_B", intrinsincDict=intrinsic_dict, plot_name="Mag_B")

###################################################################################################
# Save and solve
M3D.save_project()
M3D.analyze_all()

####################################################################################################
# The electronics desktop is released from the PyAEDT scripting
# We can leave the 'desktop' and 'project' open after the above script has run by setting (False, False) below.
M3D.release_desktop(True, True)
