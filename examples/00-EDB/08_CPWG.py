"""
EDB: fully parameterized CPWG design
------------------------------------
This example shows how to use HFSS 3D Layout to create a parametric design
for a CPWG (coplanar waveguide with ground).
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Peform required imports. Importing the ``Hfss3dlayout`` object initializes it
# on version 2022 R2.

import tempfile
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt import Hfss3dLayout
import os
import numpy as np

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch EDB.

tmpfold = tempfile.gettempdir()
aedb_path = os.path.join(tmpfold, generate_unique_name("pcb") + ".aedb")
print(aedb_path)
edbapp = Edb(edbpath=aedb_path, edbversion="2022.2")

# Define parameters
# ~~~~~~~~~~~~~~~~~
# Define parameters.

params = {"$ms_width": "0.4mm",
          "$ms_clearance": "0.3mm",
          "$ms_length": "20mm",
          }
for par_name in params:
    edbapp.add_design_variable(par_name, params[par_name])

# Create stackup
# ~~~~~~~~~~~~~~
# Create a symmetric stackup.

edbapp.core_stackup.create_symmetric_stackup(2)

# Draw planes
# ~~~~~~~~~~~
# Draw planes.

plane_lw_pt = ["0mm", "-3mm"]
plane_up_pt = ["$ms_length", "3mm"]

top_layer_obj = edbapp.core_primitives.create_rectangle("TOP", net_name="gnd",
                                                        lower_left_point=plane_lw_pt,
                                                        upper_right_point=plane_up_pt)
bot_layer_obj = edbapp.core_primitives.create_rectangle("BOTTOM", net_name="gnd",
                                                        lower_left_point=plane_lw_pt,
                                                        upper_right_point=plane_up_pt)
layer_dict = {"TOP": top_layer_obj,
              "BOTTOM": bot_layer_obj}

# Draw trace
# ~~~~~~~~~~
# Draw a trace.

trace_path = [["0", "0"], ["$ms_length", "0"]]
edbapp.core_primitives.create_trace(trace_path,
                                    layer_name="TOP",
                                    width="$ms_width",
                                    net_name="sig",
                                    start_cap_style="Flat",
                                    end_cap_style="Flat"
                                    )

# Create trace to plane clearance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a trace to the plane clearance.

poly_void = edbapp.core_primitives.create_trace(trace_path, layer_name="TOP", net_name="gnd",
                                                width="{}+2*{}".format("$ms_width", "$ms_clearance"),
                                                start_cap_style="Flat",
                                                end_cap_style="Flat")
edbapp.core_primitives.add_void(layer_dict["TOP"], poly_void)

# Create ground via padstack and place ground stitching vias
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a ground via padstack and place ground stitching vias.

edbapp.core_padstack.create_padstack(padstackname="GVIA",
                                     holediam="0.3mm",
                                     paddiam="0.5mm",
                                     )

yloc_u = "$ms_width/2+$ms_clearance+0.25mm"
yloc_l = "-$ms_width/2-$ms_clearance-0.25mm"

for i in np.arange(1, 20):
    edbapp.core_padstack.place_padstack([str(i) + "mm", yloc_u], "GVIA", net_name="GND")
    edbapp.core_padstack.place_padstack([str(i) + "mm", yloc_l], "GVIA", net_name="GND")

# Save and close EDB
# ~~~~~~~~~~~~~~~~~~
# Save and close EDB.

edbapp.save_edb()
edbapp.close_edb()

###############################################################################
# Open EDB in AEDT
# ~~~~~~~~~~~~~~~~
# Op3n EDB in AEDT.

h3d = Hfss3dLayout(projectname=os.path.join(aedb_path, "edb.def"), specified_version="2022.2",
                   non_graphical=non_graphical)

###############################################################################
# Create wave ports
# ~~~~~~~~~~~~~~~~~
# Create wave ports.

h3d.create_edge_port("line_3", 0, iswave=True, wave_vertical_extension=10, wave_horizontal_extension=10)
h3d.create_edge_port("line_3", 2, iswave=True, wave_vertical_extension=10, wave_horizontal_extension=10)

###############################################################################
# Edit airbox extents
# ~~~~~~~~~~~~~~~~~~~
# Edit airbox extents.

h3d.edit_hfss_extents(air_vertical_positive_padding="10mm",
                      air_vertical_negative_padding="1mm")

###############################################################################
# Create setup
# ~~~~~~~~~~~~
# Create an HFSS simulation setup.

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
# Start the HFSS solver by uncommenting the ``h3d.analyze_nominal()`` command.

# h3d.analyze_nominal()

# Release AEDT
# ~~~~~~~~~~~~
# Release AEDT.

h3d.release_desktop()