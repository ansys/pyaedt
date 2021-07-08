"""

Dipole Antenna Example
--------------------------------------------
This tutorial shows how you can use PyAedt to create an antenna setup in HFSS and post process results
"""
# sphinx_gallery_thumbnail_path = 'Resources/Dipole.png'

import os
from pyaedt import Hfss
from pyaedt import Desktop
from pyaedt import generate_unique_name

if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
#####################################################
# Start Desktop in Graphical mode
#
nongraphical = False
d = Desktop("2021.1", NG=nongraphical)

#####################################################
# Start HFSS in Graphical mode
#
hfss=Hfss()

#####################################################
# Define dipole length variable

hfss['l_dipole'] = "13.5cm"

#####################################################
# Get 3D Component from syslib
# ---------------------------------
# in order to run correctly user needs to get all the geometry parameters of the 3D component or needs to create a
# dictionary of parameters in case of encrypted 3D Component

compfile = hfss.components3d['Dipole_Antenna_DM']
geometryparams = hfss.get_components3d_vars('Dipole_Antenna_DM')
geometryparams['dipole_length'] = "l_dipole"
hfss.modeler.primitives.insert_3d_component(compfile, geometryparams)

#####################################################
# Create Boundaries
# ---------------------------------
# A region with openings is needed to run analysis

hfss.create_open_region(Frequency="1GHz")

#####################################################
# Create Setup
# ---------------------------------
# A setup with sweep will be used to run simulation

setup = hfss.create_setup("MySetup", hfss.SimulationSetupTypes.HFSSDrivenAuto)
setup.props["Type"] = "Interpolating"
setup.props["Sweeps"]['Sweep']['RangeType'] = 'LinearCount'
setup.props["Sweeps"]['Sweep']['RangeStart'] = '0.5GHz'
setup.props["Sweeps"]['Sweep']['RangeEnd'] = '1.5GHz'
setup.props["Sweeps"]['Sweep']['RangeCount'] = 401
setup.props["Sweeps"]['Sweep']['AutoSolverSetting'] = "Higher Speed"
setup.update()

#####################################################
# Save and run the simulation

hfss.save_project(os.path.join(temp_folder, "MyDipole.aedt"))
hfss.analyze_setup("MySetup")

#####################################################
# PostProcessing
# ------------------------
# We will generate a scattering plot and a Far Field Plot

hfss.create_scattering("MyScattering")
variations = hfss.available_variations.nominal_w_values_dict
variations["Freq"] = ["1GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
hfss.post.create_rectangular_plot("db(GainTotal)",hfss.nominal_adaptive, variations, "Theta", "3D",plottype="Far Fields")

#####################################################
# Close Desktop
if os.name != "posix":
    d.force_close_desktop()


