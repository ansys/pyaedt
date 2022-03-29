"""
2D Extractor: Stripline Analysis
--------------------------------
This example shows how you can use PyAEDT to create a differential stripline design in
in Q2D and run a simulation.
"""

import os

from pyaedt import Q2d
from pyaedt.generic.general_methods import generate_unique_name

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch
# AEDT in graphical mode.

NonGraphical = True

home = os.path.expanduser("~")
workdir = os.path.join(home, "Downloads", "pyaedt_example")
project_path = os.path.join(workdir, generate_unique_name("pyaedt_q2d_example") + ".aedt")

###############################################################################
# Launch AEDT and Q2D
# ~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2022.1 in graphical mode.

# This example uses SI units.


q = Q2d(projectname=project_path, designname="differential_stripline",
        specified_version="2022.1", non_graphical=NonGraphical, new_desktop_session=True)

###############################################################################
# Create variables

e_factor = "e_factor"
sig_w = "sig_bot_w"
sig_gap = "sig_gap"
co_gnd_w = "gnd_w"
clearance = "clearance"
cond_h = "cond_h"
core_h = "core_h"
pp_h = "pp_h"

for var_name, var_value in {
    "e_factor": "2",
    "sig_bot_w": "150um",
    "sig_gap": "150um",
    "gnd_w": "500um",
    "clearance": "150um",
    "cond_h": "17um",
    "core_h": "150um",
    "pp_h": "150um",

}.items():
    q[var_name] = var_value

delta_w_half = "({0}/{1})".format(cond_h, e_factor)
sig_top_w = "({1}-{0}*2)".format(delta_w_half, sig_w)
co_gnd_top_w = "({1}-{0}*2)".format(delta_w_half, co_gnd_w)
model_w = "{}*2+{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_w, sig_gap)

###############################################################################
# Create Primitives
###############################################################################
# Define layer heights

layer_1_lh = 0
layer_1_uh = cond_h
layer_2_lh = layer_1_uh + "+" + core_h
layer_2_uh = layer_2_lh + "+" + cond_h
layer_3_lh = layer_2_uh + "+" + pp_h
layer_3_uh = layer_3_lh + "+" + cond_h

###############################################################################
# Create positive signal
base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_p")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])
q.modeler.move([base_line_obj], ["{}+{}".format(co_gnd_w, clearance), 0, 0])

# Create negative signal
base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [sig_w, layer_2_lh, 0]], name="signal_n")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [sig_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])
q.modeler.move([base_line_obj], ["{}+{}+{}+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0])

###############################################################################
# Create coplanar ground
base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_left")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])

base_line_obj = q.modeler.create_polyline([[0, layer_2_lh, 0], [co_gnd_w, layer_2_lh, 0]], name="co_gnd_right")
top_line_obj = q.modeler.create_polyline([[0, layer_2_uh, 0], [co_gnd_top_w, layer_2_uh, 0]])
q.modeler.move([top_line_obj], [delta_w_half, 0, 0])
q.modeler.connect([base_line_obj, top_line_obj])
q.modeler.move([base_line_obj], ["{}+{}*2+{}*2+{}".format(co_gnd_w, clearance, sig_w, sig_gap), 0, 0])

###############################################################################
# Create reference ground plane
q.modeler.create_rectangle(position=[0, layer_1_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_u")
q.modeler.create_rectangle(position=[0, layer_3_lh, 0], dimension_list=[model_w, cond_h], name="ref_gnd_l")

###############################################################################
# Create dielectric
q.modeler.create_rectangle(
    position=[0, layer_1_uh, 0], dimension_list=[model_w, core_h], name="Core", matname="FR4_epoxy"
)
q.modeler.create_rectangle(
    position=[0, layer_2_uh, 0], dimension_list=[model_w, pp_h], name="Prepreg", matname="FR4_epoxy"
)
q.modeler.create_rectangle(
    position=[0, layer_2_lh, 0], dimension_list=[model_w, cond_h], name="Filling", matname="FR4_epoxy"
)

###############################################################################
# Assign conductors
###############################################################################
# Signal

obj = q.modeler.get_object_from_name("signal_p")
q.assign_single_conductor(
    name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
)

obj = q.modeler.get_object_from_name("signal_n")
q.assign_single_conductor(
    name=obj.name, target_objects=[obj], conductor_type="SignalLine", solve_option="SolveOnBoundary", unit="mm"
)

# Reference ground
obj = [q.modeler.get_object_from_name(i) for i in ["co_gnd_left", "co_gnd_right", "ref_gnd_u", "ref_gnd_l"]]
q.assign_single_conductor(
    name="gnd", target_objects=obj, conductor_type="ReferenceGround", solve_option="SolveOnBoundary", unit="mm"
)

###############################################################################
# Assign Huray model on signal
obj = q.modeler.get_object_from_name("signal_p")
q.assign_huray_finitecond_to_edges(obj.edges, radius="0.5um", ratio=3, name="b_" + obj.name)

obj = q.modeler.get_object_from_name("signal_n")
q.assign_huray_finitecond_to_edges(obj.edges, radius="0.5um", ratio=3, name="b_" + obj.name)

###############################################################################
# Define diff pair

matrix = q.insert_reduced_matrix(q.MATRIXOPERATIONS.DiffPair, ["signal_p", "signal_n"], rm_name="diff_pair")

###############################################################################
# Create setup and analysis

setup = q.create_setup(setupname="new_setup")

sweep = setup.add_sweep(sweepname="sweep1", sweeptype="Discrete")
sweep.props["RangeType"] = "LinearStep"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeStep"] = "100MHz"
sweep.props["RangeEnd"] = "5GHz"
sweep.props["SaveFields"] = False
sweep.props["SaveRadFields"] = False
sweep.props["Type"] = "Interpolating"
sweep.update()

# Analyze the nominal design and plot characteristic impedance

q.analyze_nominal()
plot_sources = matrix.get_sources_for_plot(category="Z0")
a = q.post.get_solution_data(expressions=plot_sources, context=matrix.name)
a.plot(snapshot_path=os.path.join(workdir, "plot.jpg")) # Save plot as jpg

# Create parametric sweep and analyze

parametric = q.parametrics.add("sig_bot_w", 75, 100, 5, "LinearStep")
parametric.add_variation("sig_gap", "100um", "200um", 5,variation_type="LinearCount")
q.analyze_setup(name=parametric.name)

###############################################################################
# Save the project and exit
q.save_project()
q.release_desktop()
