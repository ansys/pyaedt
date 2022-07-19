"""
EDB: fully parameterized design
-------------------------------
This example shows how to use HFSS 3D Layout to create and solve a parametric design.
"""

###############################################################################
# Import object
# ~~~~~~~~~~~~~
# Import the ``Hfss3dlayout`` object and initialize it on version 2022 R2.

import tempfile
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt import Hfss3dLayout
import os

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

##########################################################
# Launch EDB
# ~~~~~~~~~~
# Launch EDT.

tmpfold = tempfile.gettempdir()
aedb_path = os.path.join(tmpfold, generate_unique_name("pcb") + ".aedb")
print(aedb_path)
edb = Edb(edbpath=aedb_path, edbversion="2022.2")

######################################################################
# Define parameters
# ~~~~~~~~~~~~~~~~~

params = {"$ms_width": "0.4mm",
          "$sl_width": "0.2mm",
          "$ms_spacing": "0.2mm",
          "$sl_spacing": "0.1mm",
          "$via_spacing": "0.5mm",
          "$via_diam": "0.3mm",
          "$pad_diam": "0.6mm",
          "$anti_pad_diam": "0.7mm",
          "$pcb_len": "30mm",
          "$pcb_w": "5mm",
          "$x_size": "1.2mm",
          "$y_size": "1mm",
          "$corner_rad": "0.5mm"}

for par_name in params:
    edb.add_design_variable(par_name, params[par_name])

######################################################################
# Define stackup layers
# ~~~~~~~~~~~~~~~~~~~~~
# Define stackup layers from bottom to top.
# Note that in the stackup definition, layer_type = (0:signal, 1:dielectric).

layers = [{"name": "bottom", "layer_type": 0, "thickness": "35um", "material": "copper"},
          {"name": "diel_3", "layer_type": 1, "thickness": "275um", "material": "FR4_epoxy"},
          {"name": "sig_2", "layer_type": 0, "thickness": "35um", "material": "copper"},
          {"name": "diel_2", "layer_type": 1, "thickness": "275um", "material": "FR4_epoxy"},
          {"name": "sig_1", "layer_type": 0, "thickness": "35um", "material": "copper"},
          {"name": "diel_1", "layer_type": 1, "thickness": "275um", "material": "FR4_epoxy"},
          {"name": "top", "layer_type": 0, "thickness": "35um", "material": "copper"}]


# Create EDB stackup.
# Bottom layer

edb.core_stackup.stackup_layers.add_layer(layers[0]["name"],
                                          layerType=layers[0]["layer_type"],
                                          thickness=layers[0]["thickness"],
                                          material=layers[0]["material"])  # Insert first layer
# All subsequent layers

for n in range(len(layers)-1):
    edb.core_stackup.stackup_layers.add_layer(layers[n+1]["name"],
                                              layers[n]["name"],
                                              layerType=layers[n+1]["layer_type"],
                                              thickness=layers[n+1]["thickness"],
                                              material=layers[n+1]["material"])

###############################################################################
# Create padstack for signal via
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a parameterized padstack for the signal via.

signal_via_padstack = "automated_via"
edb.core_padstack.create_padstack(
            padstackname=signal_via_padstack,
            holediam="$via_diam",
            paddiam="$pad_diam",
            antipaddiam="",
            startlayer="top",
            endlayer="bottom",
            antipad_shape="Bullet",
            x_size="$x_size",
            y_size="$y_size",
            corner_radius="$corner_rad",
        )

###############################################################################
# Assign net names
# ~~~~~~~~~~~~~~~~
# # Assign net names. There are only two signal nets.

net_p = "p"
net_n = "n"

###############################################################################
# Place signal vias
# ~~~~~~~~~~~~~~~~~
# Place signal vias.

edb.core_padstack.place_padstack(
            position=["$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing)/2"],
            definition_name=signal_via_padstack,
            net_name=net_p,
            via_name="",
            rotation=90.0,
            fromlayer=layers[-1]["name"],
            tolayer=layers[0]["name"],)

edb.core_padstack.place_padstack(
            position=["2*$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing)/2"],
            definition_name=signal_via_padstack,
            net_name=net_p,
            via_name="",
            rotation=90.0,
            fromlayer=layers[-1]["name"],
            tolayer=layers[0]["name"],)

edb.core_padstack.place_padstack(
            position=["$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing)/2"],
            definition_name=signal_via_padstack,
            net_name=net_n,
            via_name="",
            rotation=-90.0,
            fromlayer=layers[-1]["name"],
            tolayer=layers[0]["name"],)

edb.core_padstack.place_padstack(
            position=["2*$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing)/2"],
            definition_name=signal_via_padstack,
            net_name=net_n,
            via_name="",
            rotation=-90.0,
            fromlayer=layers[-1]["name"],
            tolayer=layers[0]["name"],)


# ###############################################################################
# Draw parameterized traces
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Draw parameterized traces.
# Trace the width and the routing (Microstrip-Stripline-Microstrip).
# Applies to both p and n nets.

width = ["$ms_width", "$sl_width", "$ms_width"]                       # Trace width, n and p
route_layer = [layers[-1]["name"], layers[4]["name"], layers[-1]["name"]]    # Routing layer, n and p

# Define points for three traces in the "p" net

points_p = [
           [["0.0", "($ms_width+$ms_spacing)/2"],
            ["$pcb_len/3-2*$via_spacing", "($ms_width+$ms_spacing)/2"],
            ["$pcb_len/3-$via_spacing", "($ms_width+$ms_spacing+$via_spacing)/2"],
            ["$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing)/2"],
           ],
           [["$pcb_len/3", "($ms_width+$sl_spacing+$via_spacing)/2"],
            ["$pcb_len/3+$via_spacing", "($ms_width+$sl_spacing+$via_spacing)/2"],
            ["$pcb_len/3+2*$via_spacing", "($sl_width+$sl_spacing)/2"],
            ["2*$pcb_len/3-2*$via_spacing", "($sl_width+$sl_spacing)/2"],
            ["2*$pcb_len/3-$via_spacing", "($ms_width+$sl_spacing+$via_spacing)/2"],
            ["2*$pcb_len/3", "($ms_width+$sl_spacing+$via_spacing)/2"],
           ],
           [["2*$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing)/2"],
            ["2*$pcb_len/3+$via_spacing", "($ms_width+$ms_spacing+$via_spacing)/2"],
            ["2*$pcb_len/3+2*$via_spacing", "($ms_width+$ms_spacing)/2"],
            ["$pcb_len", "($ms_width+$ms_spacing)/2"],
           ],
          ]

# Define points for three traces in the "n" net

points_n = [
          [["0.0", "-($ms_width+$ms_spacing)/2"],
           ["$pcb_len/3-2*$via_spacing", "-($ms_width+$ms_spacing)/2"],
           ["$pcb_len/3-$via_spacing", "-($ms_width+$ms_spacing+$via_spacing)/2"],
           ["$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing)/2"],
          ],
          [["$pcb_len/3", "-($ms_width+$sl_spacing+$via_spacing)/2"],
           ["$pcb_len/3+$via_spacing", "-($ms_width+$sl_spacing+$via_spacing)/2"],
           ["$pcb_len/3+2*$via_spacing", "-($ms_width+$sl_spacing)/2"],
           ["2*$pcb_len/3-2*$via_spacing", "-($ms_width+$sl_spacing)/2"],
           ["2*$pcb_len/3-$via_spacing", "-($ms_width+$sl_spacing+$via_spacing)/2"],
           ["2*$pcb_len/3", "-($ms_width+$sl_spacing+$via_spacing)/2"],
          ],
          [["2*$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing)/2"],
           ["2*$pcb_len/3 + $via_spacing", "-($ms_width+$ms_spacing+$via_spacing)/2"],
           ["2*$pcb_len/3 + 2*$via_spacing", "-($ms_width+$ms_spacing)/2"],
           ["$pcb_len", "-($ms_width + $ms_spacing)/2"],
          ],
         ]

# Add traces to EDB

for n in range(len(points_p)):
    path_p = edb.core_primitives.Shape("polygon", points=points_p[n])
    edb.core_primitives.create_path(path_p, route_layer[n], width[n], net_name=net_p,
                                    start_cap_style="Flat", end_cap_style="Flat")
    path_n = edb.core_primitives.Shape("polygon", points=points_n[n])
    edb.core_primitives.create_path(path_n, route_layer[n], width[n], net_name=net_n,
                                    start_cap_style="Flat", end_cap_style="Flat")


###############################################################################
# Draw ground polygons
# ~~~~~~~~~~~~~~~~~~~~
# Draw ground polygons.

gnd_poly = [[0.0, "-$pcb_w/2"],
            ["$pcb_len", "-$pcb_w/2"],
            ["$pcb_len", "$pcb_w/2"],
            [0.0, "$pcb_w/2"]]
gnd_shape = edb.core_primitives.Shape("polygon", points=gnd_poly)

# Void in ground for traces on the signal routing layer

void_poly = [["$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2-$via_spacing/2"],
             ["$pcb_len/3 + $via_spacing", "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2-$via_spacing/2"],
             ["$pcb_len/3 + 2*$via_spacing",
             "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2"],
             ["2*$pcb_len/3 - 2*$via_spacing",
             "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2"],
             ["2*$pcb_len/3 - $via_spacing",
             "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2-$via_spacing/2"],
             ["2*$pcb_len/3", "-($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2-$via_spacing/2"],
             ["2*$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2+$via_spacing/2"],
             ["2*$pcb_len/3 - $via_spacing", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2+$via_spacing/2"],
             ["2*$pcb_len/3 - 2*$via_spacing", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2"],
             ["$pcb_len/3 + 2*$via_spacing", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2"],
             ["$pcb_len/3 + $via_spacing", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2+$via_spacing/2"],
             ["$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2+$via_spacing/2"],
             ["$pcb_len/3", "($ms_width+$ms_spacing+$via_spacing+$anti_pad_diam)/2"]]

void_shape = edb.core_primitives.Shape("polygon", points=void_poly)

# Add ground layers

for layer in layers[1:-1]:

    # add void if the layer is the signal routing layer.
    void = [void_shape] if layer["name"] == route_layer[1] else []

    edb.core_primitives.create_polygon(main_shape=gnd_shape,
                                       layer_name=layer["name"],
                                       voids=void,
                                       net_name="gnd")


###############################################################################
# Plot EDB
# ~~~~~~~~
# Plot EDB.

edb.core_nets.plot(None)

###############################################################################
# Save EDB
# ~~~~~~~~
# Save EDB.

edb.save_edb()
edb.close_edb()


###############################################################################
# Open EDB in AEDT
# ~~~~~~~~~~~~~~~~
# Open EDB in AEDT.

h3d = Hfss3dLayout(projectname=os.path.join(aedb_path, "edb.def"), specified_version="2022.2", non_graphical=non_graphical)


###############################################################################
# Create wave ports
# ~~~~~~~~~~~~~~~~~
# Create wave ports:

h3d.create_wave_port_from_two_conductors(["line_0", "line_1"], [0, 0])
h3d.create_wave_port_from_two_conductors(["line_4", "line_5"], [5, 5])

###############################################################################
# Add HFSS simulation setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Add HFSS simulation setup.

setup = h3d.create_setup()
h3d.create_linear_count_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=0,
    freqstop=10,
    num_of_freq_points=1001,
    sweepname="sweep1",
    sweep_type="Interpolating",
    interpolation_tol_percent=1,
    interpolation_max_solutions=255,
    save_fields=False,
    use_q3d_for_dc=False,
)


###############################################################################
# Start HFSS solver
# ~~~~~~~~~~~~~~~~~
# Start HFSS solver. Uncomment to solve.

# h3d.analyze_nominal()

h3d.release_desktop()

###############################################################################
# Note that the ground nets are only connected to each other due
# to the wave ports. The problem with poor grounding can be seen in the
# S-parameters. Try to modify this script to add ground vias and eliminate
# the resonance.
