"""
SBR+: HFSS to SBR+ coupling
---------------------------
This example shows how you can use PyAEDT to create an HFSS SBR+ project from an
HFSS antenna and run a simulation.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perrform rquired imports and set up the local path to the path for the PyAEDT
# directory.

import os
from pyaedt import examples, generate_unique_project_name
from pyaedt import Hfss

project_full_name = examples.download_sbr(generate_unique_project_name(project_name="sbr_freq"))


###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Define designs
# ~~~~~~~~~~~~~~
# Define two designs, one source and one target, with each design connected to
# a different object.

target = Hfss(
    projectname=project_full_name,
    designname="Cassegrain_",
    solution_type="SBR+",
    specified_version="2022.2",
    new_desktop_session=True,
    non_graphical=non_graphical
)
source = Hfss(projectname=target.project_name, designname="feeder", specified_version="2022.2", new_desktop_session=False)

###############################################################################
# Define linked antenna
# ~~~~~~~~~~~~~~~~~~~~~~~
# Define a linked antenna. This is HFSS far field applied to HFSS SBR+.

target.create_sbr_linked_antenna(source, target_cs="feederPosition", fieldtype="farfield")

###############################################################################
# Assign boundaries
# ~~~~~~~~~~~~~~~~~
# Assign boundaries.

target.assign_perfecte_to_sheets(["Reflector", "Subreflector"])
target.mesh.assign_curvilinear_elements(["Reflector", "Subreflector"])


###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

source.plot(show=False, export_path=os.path.join(target.working_directory, "Image.jpg"), plot_air_objects=True)


###############################################################################
# Create setup and solve
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create a setup and solve it.

setup1 = target.create_setup()
setup1.props["RadiationSetup"] = "ATK_3D"
setup1.props["ComputeFarFields"] = True
setup1.props["RayDensityPerWavelength"] = 2
setup1.props["MaxNumberOfBounces"] = 3
setup1["RangeType"] = "SinglePoints"
setup1["RangeStart"] = "10GHz"
target.analyze_nominal()

###############################################################################
# Plot results
# ~~~~~~~~~~~~
# Plot results.

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
# Plot results outside AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot results using Matplotlib.

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
# Release AEDT
# ~~~~~~~~~~~~
# Release AEDT and close the example.

if os.name != "posix":
    target.release_desktop()
