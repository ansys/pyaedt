"""
Hfss 3D Layout: Parametric Via Analysis
---------------------------------------
This example shows how to use HFSS 3D Layout to create and solve a parametric design.
"""
# sphinx_gallery_thumbnail_path = 'Resources/3dlayout.png'

###############################################################################
# # Import the `Hfss3dlayout` Object
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example imports the `Hfss3dlayout` object and initializes it on version
# 2022R1.

from pyaedt import Hfss3dLayout
import os

h3d = Hfss3dLayout(specified_version="2022.1", new_desktop_session=True, non_graphical=True)

###############################################################################
# Set Up Parametric Variables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example sets up all parametric variables to use in the layout.

h3d["viatotrace"] = "5mm"
h3d["viatovia"] = "10mm"
h3d["w1"] = "1mm"
h3d["sp"] = "0.5mm"
h3d["len"] = "50mm"

###############################################################################
# Create a Stackup
# ~~~~~~~~~~~~~~~~
# This example creates a stackup.

h3d.modeler.layers.add_layer("GND", "signal", thickness="0", isnegative=True)
h3d.modeler.layers.add_layer("diel", "dielectric", thickness="0.2mm", material="FR4_epoxy")
h3d.modeler.layers.add_layer("TOP", "signal", thickness="0.035mm", elevation="0.2mm")

###############################################################################
# Create a Signal Net and Ground Planes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example create a signal net and ground planes.

h3d.modeler.create_line("TOP", [[0, 0], ["len", 0]], lw="w1", netname="microstrip", name="microstrip")
h3d.modeler.create_rectangle("TOP", [0, "-w1/2-sp"], ["len", "-w1/2-sp-20mm"])
h3d.modeler.create_rectangle("TOP", [0, "w1/2+sp"], ["len", "w1/2+sp+20mm"])

###############################################################################
# Create Vias with Parametric Positions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates vias with parametric positions.

h3d.modeler.create_via(x="viatovia", y="-viatotrace", name="via1")
h3d.modeler.create_via(x="viatovia", y="viatotrace", name="via2")
h3d.modeler.create_via(x="2*viatovia", y="-viatotrace")
h3d.modeler.create_via(x="2*viatovia", y="viatotrace")
h3d.modeler.create_via(x="3*viatovia", y="-viatotrace")
h3d.modeler.create_via(x="3*viatovia", y="viatotrace")

###############################################################################
# Add Circuit Ports
# ~~~~~~~~~~~~~~~~~
# This example adds circuit ports to the setup.

h3d.create_edge_port("microstrip", 0)
h3d.create_edge_port("microstrip", 2)

###############################################################################
# Create a Setup and Sweep
# ~~~~~~~~~~~~~~~~~~~~~~~~
# This example create a setup and sweep.

setup = h3d.create_setup()
h3d.create_linear_count_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=3,
    freqstop=7,
    num_of_freq_points=1001,
    sweepname="sweep1",
    sweep_type="Interpolating",
    interpolation_tol_percent=1,
    interpolation_max_solutions=255,
    save_fields=False,
    use_q3d_for_dc=False,
)

###############################################################################
# Solve and Plot Results
# ~~~~~~~~~~~~~~~~~~~~~~
# This example solves and plots results.

h3d.analyze_nominal()
traces = h3d.get_traces_for_plot(first_element_filter="Port1")
h3d.post.create_report(traces, families_dict=h3d.available_variations.nominal_w_values_dict)

###############################################################################
# Create Report outside AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Report using Matplotlib.
traces = h3d.get_traces_for_plot(first_element_filter="Port1", category="S")

solutions = h3d.post.get_solution_data(expressions=traces)
solutions.plot(math_formula="db20")


###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.

if os.name != "posix":
    h3d.release_desktop()
