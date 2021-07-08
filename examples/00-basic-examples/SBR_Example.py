"""

SBR+ Example
--------------------------------------------
This tutorial shows how you can use PyAedt to create a BusBar Project in
in Q3D and run a simulation
"""
#########################################################
# Import Packages
# Setup The local path to the Path Containing AEDTLIb
import os

from pyaedt import examples, generate_unique_name
project_full_name = examples.download_sbr()
project_name = os.path.basename(project_full_name)[:-5]
if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("SBR"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
from pyaedt import Hfss
#####################################
# Define 2 Design. One Source and one Target, each one connected to different object
target = Hfss(projectname=project_full_name, designname="Cassegrain_", solution_type="SBR+", specified_version="2021.1", AlwaysNew=False)
target.save_project(os.path.join(temp_folder,project_name+".aedt"))
source = Hfss(projectname=project_name, designname="feeder", specified_version="2021.1", AlwaysNew=False)

#####################################
# Define Linked Antenna. This is Hfss Far Field Applied to SBR+
target.create_sbr_linked_antenna(source, target_cs="feederPosition", fieldtype="farfield")

#####################################
# Assign Boundaries
target.assign_perfecte_to_sheets(["Reflector","Subreflector"])
target.mesh.assign_curvilinear_elements(["Reflector", "Subreflector"])
#####################################
# Create Setup  and Solve
setup1=target.create_setup()
setup1.props["RayDensityPerWavelength"]=2
setup1.props["ComputeFarFields"]=True
setup1.props["MaxNumberOfBounces"]=3
setup1.props["Sweeps"]["Sweep"]["RangeType"]="SinglePoints"
setup1.props["Sweeps"]["Sweep"]["RangeStart"]="10GHz"
setup1.props["RadiationSetup"]="ATK_3D"
setup1.update()
target.analyse_nominal()

#####################################
# Plot Results
variations = target.available_variations.nominal_w_values_dict
variations["Freq"] = ["10GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
target.post.create_rectangular_plot("db(GainTotal)",target.nominal_adaptive, variations, "Theta", "ATK_3D",plottype="Far Fields")
if os.name != "posix":
    target.close_desktop()