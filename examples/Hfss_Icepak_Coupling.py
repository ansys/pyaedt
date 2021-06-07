"""

HFSS-Icepack Coupling Analysis
--------------------------------------------
This Example shows how to create a full project from scratch in HFSS and Icepak (linked to HFSS). the project creates
a setup, solves it and create post processing output. It includes a lot of commands to show pyaedt Capabilitiesn
"""



import os
import sys
import pathlib
import glob
from IPython.display import Image

local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
pdf_path1 =  os.path.join(aedt_lib_path, "pyaedt", "core", "Dlls", "PDFReport")
sys.path.append(os.path.join(module_path))
sys.path.append(os.path.join(aedt_lib_path))
sys.path.append(os.path.join(pdf_path1))
from pyaedt import generate_unique_name
project_dir = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(project_dir): os.makedirs(project_dir)
print(project_dir)



from pyaedt import Hfss
from pyaedt import Icepak
from pyaedt import Desktop
import numpy as np
import matplotlib.pyplot as plt


###############################################################################
# Launch Desktop and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples will use AEDT 2021.1 in Graphical mode

# This examples will use SI units.


desktopVersion = "2021.1"
###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode

NonGraphical = True
NewThread = False
project_name = "Test_Jupyter_NG"
project_file = os.path.join(project_dir, project_name + ".aedt")

################################################################
# Launch Electronics Desktop and Initialize HFSS app the command
# Initializes the HFSS Design in AEDT.
# If there is a running HFSS Design the aedtapp will be linked to it, otherwise a new design will be run.

desktop=Desktop(desktopVersion, NonGraphical, NewThread)
aedtapp = Hfss()

################################################################
# Variables Settings
# A variable can be initialized simpy by creating it as a list object.
# If user enter $ then the variable will be created for project otherwise for design.


aedtapp["$coax_dimension"] = "100mm"
aedtapp.save_project(project_file)
udp = aedtapp.modeler.Position(0, 0, 0)
aedtapp["inner"] = "3mm"

################################################################
# Modeler
# Create the Coaxial, 3 Cylinders.
# Parameters can be applied directly to create_cylinder method,
# also material can be assigned directly to the object creation action.
# Alternatively the material can be assigned usign assignmaterial function


id1 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, "inner", "$coax_dimension",
                                                 0, "inner")
id2 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, 8, "$coax_dimension",
                                                 0, matname="teflon_based")
id3 = aedtapp.modeler.primitives.create_cylinder(aedtapp.CoordinateSystemPlane.XYPlane, udp, 10, "$coax_dimension",
                                                 0, "outer")

################################################################
# Material Assigment
# User can assign material directly when creating primitive, as done for id2 or assign after the object has been created

aedtapp.assignmaterial([id1, id3], "Copper")

################################################################
# Modeler Operations
# Subtract, add, etc. can be done using id of object or object name


aedtapp.modeler.subtract(id3, id2, True)
aedtapp.modeler.subtract(id2, id1, True)

################################################################
# Mesh Operations
# Most of the mesh operations are already available.
# After created, a mesh operation is accessible for edit or review of parameters

aedtapp.mesh.assign_initial_mesh_from_slider(6)
aedtapp.mesh.assign_model_resolution([aedtapp.modeler.primitives.get_obj_name(id1), aedtapp.modeler.primitives.get_obj_name(id3)], None)
aedtapp.mesh.assign_length_mesh(aedtapp.modeler.primitives.get_object_faces(id2), False, 1, 2000)

################################################################
# Automatic Excitations Creation
# this method will automatically identify the closest faces on predefined direction and create a sheet to cover that faces and
# will assign a port to that face. If selected, the method will also create a PEC cap


aedtapp.create_wave_port_between_objects("inner", "outer",axisdir=0, add_pec_cap=True, portname="P1")
aedtapp.create_wave_port_between_objects("inner", "outer",axisdir=3, add_pec_cap=True, portname="P2")

portnames = aedtapp.get_all_sources()
aedtapp.modeler.fit_all()

################################################################
# Setup Generation
# Setup is created with defaults values. after created user can apply any change and update setup when done.
# The update method returns a boolean


aedtapp.set_active_design(aedtapp.design_name)
setup = aedtapp.create_setup("MySetup")
setup.props["Frequency"] = "1GHz"
setup.props["BasisOrder"] = 2
setup.props["MaximumPasses"] = 1
setup.update()

################################################################
# Sweep Generation
# Sweep is created with defaults values.

sweepname = aedtapp.create_frequency_sweep("MySetup", "GHz", 0.8, 1.2)

################################################################
# ICEPAK Model Creation. After HFSS Setup is ready it will be linked to an icepak project to run a coupled physics analysis
# ipkapp.copy_solid_bodies_from(aedtapp) will import model from HFSS with all material settings

ipkapp = Icepak()
ipkapp.copy_solid_bodies_from(aedtapp)

################################################################
# After the model is imported we need to link sources to EM Losses


surfaceobj = ["inner", "outer"]
ipkapp.assign_em_losses(aedtapp.design_name, "MySetup", "LastAdaptive", "1GHz", surfaceobj, paramlist=["$coax_dimension","inner"])

################################################################
# Gravity setting is important for a fluid analysis

ipkapp.edit_design_settings(aedtapp.GravityDirection.ZNeg)

################################################################
# Setup Project in Icepak
# When you create a setup, default settings will be applied
# When you need to change a property of the setup you can use props command and pass the right value to the property value.
# The update function will apply the settings to the setup
# Setup creation process is identical for all tools


setup_ipk = ipkapp.create_setup("SetupIPK")
setup_ipk.props["Convergence Criteria - Max Iterations"] = 3
setup_ipk.update()

################################################################
# Mesh Settings
# After created, a mesh operation is accessible for edit or review of parameters

airbox = ipkapp.modeler.primitives.get_obj_id("Region")
ipkapp.modeler.primitives[airbox].display_wireframe(True)
airfaces = ipkapp.modeler.primitives.get_object_faces(airbox)
ipkapp.assign_openings(airfaces)

################################################################
# Cloase and Open Projects
# This command shows how to save, close and load projects.
# This can be helpful in case of operations on multiple projects.

aedtapp.save_project()
aedtapp.close_project(project_name)
aedtapp.load_project(project_file)
ipkapp = Icepak()
ipkapp.solution_type = ipkapp.SolutionTypes.Icepak.SteadyTemperatureAndFlow
ipkapp.modeler.fit_all()

################################################################
# Solve Icepak
# Icepak will solve also
# Solve HFSS Sweep when Icepak is finished

setup1 = ipkapp.analyze_setup("SetupIPK")
aedtapp.save_project()
aedtapp.modeler.fit_all()
aedtapp.analyze_setup("MySetup")

################################################################
# Plot and Export
# Generating images and Field Plots
# This section we generate Field Plots on HFSS Projects and we export it as an image

cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
vollist = [aedtapp.modeler.primitives.get_obj_name(id2)]
setup_name = "MySetup : LastAdaptive"
quantity_name = "ComplexMag_E"
quantity_name2 = "ComplexMag_H"
intrinsic = {"Freq": "1GHz", "Phase": "0deg"}
surflist = aedtapp.modeler.primitives.get_object_faces("outer")
plot1 = aedtapp.post.create_fieldplot_surface(surflist, quantity_name2, setup_name, intrinsic)

results_folder = os.path.join(aedtapp.project_path,"Coaxial_Results_NG")
if not os.path.exists(results_folder):
    os.mkdir(results_folder)

aedtapp.post.plot_field_from_fieldplot(plot1.name, project_path=results_folder, meshplot=False, setup_name=setup_name,
                                             intrinsic_dict=intrinsic, imageformat="jpg", view="iso")

################################################################
# Generating animation from Field Plots
# This section we generate Field Plots animation using Pyvista


import time
start = time.time()
cutlist = ["Global:XY"]
phases=[str(i*5)+"deg" for i in range(18)]
aedtapp.post.animate_fields_from_aedtplt_2(quantityname="Mag_E",object_list=cutlist,plottype="CutPlane",meshplot=False, setup_name=aedtapp.nominal_adaptive,intrinsic_dict={"Freq":"1GHz", "Phase":"0deg"},project_path=results_folder, variation_variable="Phase",variation_list=phases, off_screen=True,export_gif=True)
endtime = time.time() - start
print("Total Time", endtime)

################################################################
# Create Icepak Plots and export
# Functions are exactly the same as seen above for HFSS. Only the Quantity is different.


quantity_name = "Temperature"
setup_name = ipkapp.existing_analysis_sweeps[0]
intrinsic = ""
surflist = ipkapp.modeler.primitives.get_object_faces("inner")
plot5 = ipkapp.post.create_fieldplot_surface(surflist, "SurfTemperature")

ipkapp.post.plot_field_from_fieldplot(plot5.name, project_path=results_folder, meshplot=False, setup_name=setup_name, imageformat="jpg", view="iso")

aedtapp.save_project()

################################################################
# Usage of Matplotlib and Numpy to generate graph outside pyaedt


trace_names = []
for el in portnames:
    for el2 in portnames:
        trace_names.append('S(' + el + ',' + el2 + ')')
cxt = ['Domain:=', 'Sweep']
families = ['Freq:=', ['All']]
my_data = aedtapp.post.get_report_data(expression=trace_names)
freq_data = np.array(my_data.sweeps["Freq"])

comp = []
fig, ax = plt.subplots(figsize=(20, 10))

ax.set(xlabel='Frequency (Ghz)', ylabel='SParameters(dB)', title='Scattering Chart')
ax.grid()
for el in trace_names:
    mag_data = np.array(my_data.data_db(el))
    ax.plot(freq_data, mag_data)
plt.savefig(os.path.join(results_folder,project_name+".svg"))
plt.savefig(os.path.join(results_folder,project_name+".jpg"))
plt.show()


################################################################
# Close AEDT and Closed Project


aedtapp.close_project(aedtapp.project_name)
desktop.force_close_desktop()



