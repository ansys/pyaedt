"""
EDB: post-layout parameterization
---------------------------------
This example shows you how to parameterize the signal net in post-layout.
"""

###############################################################################
# Define input parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
signal_net_name = "SEL_A0"
coplanar_plane_net_name = "VSHLD_S5"  # Specify coplanar plane net name for adding clearance
layers = ["LYR_2"]  # Specify layers to be parameterized

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
import os
import tempfile
import pyaedt

from pyaedt import downloads
from pyaedt import Edb

temppath = tempfile.gettempdir()

###############################################################################
# Download and open example layout file in edb format
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
edb_fpath = downloads.download_aedb()
appedb = Edb(edb_fpath, edbversion="2023.1")

###############################################################################
# Get all trace segments from the signal net
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
net = appedb.nets[signal_net_name]
trace_segments = []
for p in net.primitives:
    if p.layer_name not in layers:
        continue
    if not p.type == "Path":
        continue
    trace_segments.append(p)

###############################################################################
# Create and assign delta w variable per layer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for p in trace_segments:
    vname = f"{p.net_name}_{p.layer_name}_dw"
    if vname not in appedb.variables:
        appedb[vname] = "0mm"
    new_w = f"{p.width}+{vname}"
    p.width = new_w

###############################################################################
# Create and assign clearance variable per layer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for p in trace_segments:
    clr = f"{p.net_name}_{p.layer_name}_clr"
    if clr not in appedb.variables:
        appedb[clr] = "0.5mm"
    path = p.get_center_line()
    for g in appedb.modeler.get_polygons_by_layer(p.layer_name, coplanar_plane_net_name):
        for v in g.voids:
            if p.is_intersecting(v):
                v.delete()
        void = appedb.modeler.create_trace(path, p.layer_name, f"{p.width}+{clr}*2")
        g.add_void(void)

###############################################################################
# Cutout and plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
appedb.cutout([signal_net_name], [coplanar_plane_net_name, "GND"])
board_size_x, board_size_y = appedb.board_size
fig_size_x = 2000
fig_size_y = board_size_y*fig_size_x/board_size_x
appedb.nets.plot(layers=layers[0], size=(fig_size_x, fig_size_y))

###############################################################################
# Save and close Edb
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

save_edb_fpath = os.path.join(temppath, pyaedt.generate_unique_name("post_layout_parameterization") + ".aedb")
appedb.save_edb_as(save_edb_fpath)
print("Edb is saved to ", save_edb_fpath)
appedb.close_edb()
