"""
Sbr+: HFSS to SBR+ Coupling
---------------------------
This example shows how you can use PyAEDT to create an SBR+ project from Hfss
antenna and run a simulation.
"""
###############################################################################
# Import Packages
# ~~~~~~~~~~~~~~~
# This example sets up the local path to the path for the ``PyAEDT`` directory.

import os
import tempfile
from pyaedt import examples, generate_unique_name

project_full_name = examples.download_sbr()
project_name = os.path.basename(project_full_name)[:-5]
tmpfold = tempfile.gettempdir()


temp_folder = os.path.join(tmpfold, generate_unique_name("SBR"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
from pyaedt import Hfss

###############################################################################
# Define Designs
# ~~~~~~~~~~~~~~
# Define two designs, one source and one target, with each one connected to
# a different object.

target = Hfss(
    projectname=project_full_name,
    designname="Cassegrain_",
    solution_type="SBR+",
    specified_version="2022.1",
    new_desktop_session=True,
)
target.save_project(os.path.join(temp_folder, project_name + ".aedt"))
source = Hfss(projectname=project_name, designname="feeder", specified_version="2022.1", new_desktop_session=False)

###############################################################################
# Define a Linked Antenna
# ~~~~~~~~~~~~~~~~~~~~~~~
# This is HFSS Far Field applied to SBR+.

target.create_sbr_linked_antenna(source, target_cs="feederPosition", fieldtype="farfield")

###############################################################################
# Assign Boundaries
# ~~~~~~~~~~~~~~~~~
# These commands assign boundaries.

target.assign_perfecte_to_sheets(["Reflector", "Subreflector"])
target.mesh.assign_curvilinear_elements(["Reflector", "Subreflector"])


###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

source.plot(show=False, export_path=os.path.join(target.working_directory, "Image.jpg"), plot_air_objects=True)


###############################################################################
# Create a Setup and Solve
# ~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a setup and then solves it.

setup1 = target.create_setup()
setup1.props["RadiationSetup"] = "ATK_3D"
setup1.props["ComputeFarFields"] = True
setup1.props["RayDensityPerWavelength"] = 2
setup1.props["MaxNumberOfBounces"] = 3
setup1.props["Sweeps"]["Sweep"]["RangeType"] = "SinglePoints"
setup1.props["Sweeps"]["Sweep"]["RangeStart"] = "10GHz"
target.analyze_nominal()

###############################################################################
# Plot Results
# ~~~~~~~~~~~~
# This example plots results.

variations = target.available_variations.nominal_w_values_dict
variations["Freq"] = ["10GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
target.post.create_report(
    "db(GainTotal)",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)

###############################################################################
# Plot Results Outside Electronics Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example plots results using matplotlib.

solution = target.post.get_solution_data(
    "GainTotal",
    target.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Theta",
    context="ATK_3D",
    report_category="Far Fields",
)
solution.plot()


###############################################################################
# Close and Exit Example
# ~~~~~~~~~~~~~~~~~~~~~~
# Release desktop and close example.

if os.name != "posix":
    target.release_desktop()
