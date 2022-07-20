"""
Multiphysics: HFSS-Icepack multiphysics analysis
------------------------------------------------
This example shows how to create a full project from scratch in HFSS and Icepak (linked to HFSS).
The project creates a setup, solves it, and creates postprocessing outputs.

To provide the advanced postprocessing features needed for this example, Matplotlib, NumPy, and
PyVista must be installed on the machine.

This examples runs only on Windows using CPython.
"""
###############################################################################
# Perform required imports and set paths
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

import os
import sys
import tempfile
import pathlib


local_path = os.path.abspath("")
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
pdf_path1 = os.path.join(aedt_lib_path, "pyaedt", "core", "Dlls", "PDFReport")
sys.path.append(os.path.join(module_path))
sys.path.append(os.path.join(aedt_lib_path))
sys.path.append(os.path.join(pdf_path1))
from pyaedt import generate_unique_name
from pyaedt.generic.constants import GLOBALCS

tmpfold = tempfile.gettempdir()


project_dir = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print(project_dir)


from pyaedt import Hfss
from pyaedt import Icepak


###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode. This example uses SI units.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
desktopVersion = "2022.2"

###############################################################################
# Open project
# ~~~~~~~~~~~~
# Open the project.

NewThread = True
project_name = "HFSS_Icepak_Coupling"
project_file = os.path.join(project_dir, project_name + ".aedt")

###############################################################################
# Launch AEDT and initialize HFSS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT and initialize HFSS. If there is an active HFSS design, ``aedtapp``
# is linked to it. Otherwise, a new design is created.

aedtapp = Hfss(specified_version=desktopVersion, non_graphical=non_graphical, new_desktop_session=NewThread)

###############################################################################
# Initialize variable settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initialize variable settings. You can initialzie a variable simply by creating
# it as a list object. If you enter the prefix ``$``, the variable is created for
# the project. Otherwise, the variable is created for the design.

aedtapp["$coax_dimension"] = "100mm"
aedtapp.save_project(project_file)
udp = aedtapp.modeler.Position(0, 0, 0)
aedtapp["inner"] = "3mm"

###############################################################################
# Create coaxial and cylinders
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a coaxial and three cylinders in the modeler. You can apply parameters
# directly using the :func:`pyaedt.modeler.Primitives3D.Primitives3D.create_cylinder`
# method. You can assign a material directly to the object creation action.
# Optionally, you can assign a material using the :func:`assign_material` method.

# TODO: How does this work when two truesurfaces are defined?
o1 = aedtapp.modeler.create_cylinder(aedtapp.PLANE.ZX, udp, "inner", "$coax_dimension", numSides=0, name="inner")
o2 = aedtapp.modeler.create_cylinder(aedtapp.PLANE.ZX, udp, 8, "$coax_dimension", numSides=0, matname="teflon_based")
o3 = aedtapp.modeler.create_cylinder(aedtapp.PLANE.ZX, udp, 10, "$coax_dimension", numSides=0, name="outer")

###############################################################################
# Assign colors
# ~~~~~~~~~~~~~
# Assign colors to each primitive.

o1.color = (255, 0, 0)
o2.color = (0, 255, 0)
o3.color = (255, 0, 0)
o3.transparency = 0.8
aedtapp.modeler.fit_all()

###############################################################################
# Assign materials
# ~~~~~~~~~~~~~~~~
# Assign materials. You can assign materials either directly when creating the primitive,
# which was done for ``id2``, or after the object is created.

o1.material_name = "Copper"
o3.material_name = "Copper"

###############################################################################
# Perform modeler operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Perform modeler operations. You can subtract, add, and perform other operations
# using either the object ID or object name.

aedtapp.modeler.subtract(o3, o2, True)
aedtapp.modeler.subtract(o2, o1, True)

###############################################################################
# Perform mesh operations
# ~~~~~~~~~~~~~~~~~~~~~~~
# Perform mesh operations. Most mesh operations are available.
# After a mesh is created, you can access a mesh operation to
# edit or review parameter values.

aedtapp.mesh.assign_initial_mesh_from_slider(6)
aedtapp.mesh.assign_model_resolution([o1.name, o3.name], None)
aedtapp.mesh.assign_length_mesh(o2.faces, False, 1, 2000)

###############################################################################
# Create excitations
# ~~~~~~~~~~~~~~~~~~
# Create excitations. The ``create_wave_port_between_objects`` method automatically
# identifies the closest faces on a predefined direction and creates a sheet to cover
# the faces. It also assigns a port to this face. If ``add_pec_cap=True``, the method
# creates a PEC cap.

aedtapp.create_wave_port_between_objects("inner", "outer", axisdir=1, add_pec_cap=True, portname="P1")
aedtapp.create_wave_port_between_objects("inner", "outer", axisdir=4, add_pec_cap=True, portname="P2")

portnames = aedtapp.get_all_sources()
aedtapp.modeler.fit_all()


###############################################################################
# Create setup
# ~~~~~~~~~~~~~
# Create a setup. A setup is created with default values. After its creation,
# you can change values and update the setup. The ``update`` method returns a Boolean
# value.

aedtapp.set_active_design(aedtapp.design_name)
setup = aedtapp.create_setup("MySetup")
setup.props["Frequency"] = "1GHz"
setup.props["BasisOrder"] = 2
setup.props["MaximumPasses"] = 1

###############################################################################
# Create sweep
# ~~~~~~~~~~~~
# Create a sweep. A sweep is created with default values.

sweepname = aedtapp.create_linear_count_sweep("MySetup", "GHz", 0.8, 1.2, 401, sweep_type="Interpolating")

################################################################################
# Create Icepak model
# ~~~~~~~~~~~~~~~~~~~
# Create an Icepak model. After an HFSS setup is ready, link this model to an Icepak
# project and run a coupled physics analysis. The :func:`FieldAnalysis3D.copy_solid_bodies_from`
# method imports a model from HFSS with all material settings.

ipkapp = Icepak()
ipkapp.copy_solid_bodies_from(aedtapp)

################################################################################
# Link sources to EM losses
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Link sources to the EM losses.

surfaceobj = ["inner", "outer"]
ipkapp.assign_em_losses(
    aedtapp.design_name, "MySetup", "LastAdaptive", "1GHz", surfaceobj, paramlist=["$coax_dimension", "inner"]
)

#################################################################################
# Edit gravity setting
# ~~~~~~~~~~~~~~~~~~~~
# Edit the gravity setting if necessary because it is important for a fluid analysis.

ipkapp.edit_design_settings(aedtapp.GravityDirection.ZNeg)

################################################################################
# Set Up Icepak project
# ~~~~~~~~~~~~~~~~~~~~~
# Set up the Icepak project. When you create a setup, default settings are applied.
# When you need to change a property of the setup, you can use the ``props``
# command to pass the correct value to the property. The ``update`` function
# applies the settings to the setup. The setup creation process is identical
# for all tools.

setup_ipk = ipkapp.create_setup("SetupIPK")
setup_ipk.props["Convergence Criteria - Max Iterations"] = 3

################################################################################
# Edit or review mesh parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Edit or review the mesh parameters. After a mesh is created, you can access
# a mesh operation to edit or review parameter values.

airbox = ipkapp.modeler.get_obj_id("Region")
ipkapp.modeler[airbox].display_wireframe = True
airfaces = ipkapp.modeler.get_object_faces(airbox)
ipkapp.assign_openings(airfaces)

################################################################################
# Close and open projects
# ~~~~~~~~~~~~~~~~~~~~~~~
# Close and open the projects to ensure that the HFSS - Icepak coupling works
# correctly in AEDT versions 2019 R3 through 2021 R1. Closing and opening projects
# can be helpful when performing operations on multiple projects.

aedtapp.save_project()
aedtapp.close_project(project_name)
aedtapp = Hfss(project_file)
ipkapp = Icepak()
ipkapp.solution_type = ipkapp.SOLUTIONS.Icepak.SteadyTemperatureAndFlow
ipkapp.modeler.fit_all()

################################################################################
# Solve Icepak project
# ~~~~~~~~~~~~~~~~~~~~
# Solve the Icepak project and the HFSS sweep.

setup1 = ipkapp.analyze_setup("SetupIPK")
aedtapp.save_project()
aedtapp.modeler.fit_all()
aedtapp.analyze_setup("MySetup")

################################################################################
# Generate field plots and export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate field plots on the HFSS project and export them as images.

cutlist = [GLOBALCS.XY, GLOBALCS.ZX, GLOBALCS.YZ]
vollist = [o2.name]
setup_name = "MySetup : LastAdaptive"
quantity_name = "ComplexMag_E"
quantity_name2 = "ComplexMag_H"
intrinsic = {"Freq": "1GHz", "Phase": "0deg"}
surflist = aedtapp.modeler.get_object_faces("outer")
plot1 = aedtapp.post.create_fieldplot_surface(surflist, quantity_name2, setup_name, intrinsic)

results_folder = os.path.join(aedtapp.working_directory, "Coaxial_Results_NG")
if not os.path.exists(results_folder):
    os.mkdir(results_folder)

aedtapp.post.plot_field_from_fieldplot(
    plot1.name,
    project_path=results_folder,
    meshplot=False,
    imageformat="jpg",
    view="isometric",
    show=False,
)

################################################################################
# Generate animation from field plots
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate an animation from field plots using PyVista.

import time

start = time.time()
cutlist = ["Global:XY"]
phases = [str(i * 5) + "deg" for i in range(18)]
animated = aedtapp.post.animate_fields_from_aedtplt_2(
    quantityname="Mag_E",
    object_list=cutlist,
    plottype="CutPlane",
    meshplot=False,
    setup_name=aedtapp.nominal_adaptive,
    intrinsic_dict={"Freq": "1GHz", "Phase": "0deg"},
    project_path=results_folder,
    variation_variable="Phase",
    variation_list=phases,
    show=False,
    export_gif=False,
)
animated.gif_file = os.path.join(aedtapp.working_directory, "animate.gif")
animated.camera_position = [0, 50, 200]
animated.focal_point = [0, 50, 0]
# Set off_screen to False to visualize the animation.
# animated.off_screen = False
animated.animate()

endtime = time.time() - start
print("Total Time", endtime)

################################################################################
# Create Icepak plots and export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Icepak plots and export them as images using the same functions that
# were used early. Only the quantity is different.

quantity_name = "Temperature"
setup_name = ipkapp.existing_analysis_sweeps[0]
intrinsic = ""
surflist = ipkapp.modeler.get_object_faces("inner")
plot5 = ipkapp.post.create_fieldplot_surface(surflist, "SurfTemperature")

ipkapp.post.plot_field_from_fieldplot(
    plot5.name,
    project_path=results_folder,
    meshplot=False,
    imageformat="jpg",
    view="isometric",
    show=False,
)

aedtapp.save_project()

################################################################################
# Generate plots outside of AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Generate plots outside of AEDT using Matplotlib and Numpy.

trace_names = aedtapp.get_traces_for_plot(category="S")
cxt = ["Domain:=", "Sweep"]
families = ["Freq:=", ["All"]]
my_data = aedtapp.post.get_solution_data(expressions=trace_names)
my_data.plot(trace_names, "db20", xlabel="Frequency (Ghz)", ylabel="SParameters(dB)", title="Scattering Chart")

################################################################################
# Close project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Close the project and release AEDT.

# aedtapp.close_project(aedtapp.project_name)
aedtapp.release_desktop()
