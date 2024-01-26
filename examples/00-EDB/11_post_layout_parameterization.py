"""
EDB: post-layout parameterization
---------------------------------
This example shows you how to parameterize the signal net in post-layout.
"""

###############################################################################
# Define input parameters.
signal_net_name = "DDR4_ALERT3"
coplanar_plane_net_name = "1V0"  # Specify coplanar plane net name for adding clearance
layers = ["16_Bottom"]  # Specify layers to be parameterized

###############################################################################
# Perform required imports.
import os
import tempfile
import pyaedt

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

###############################################################################
# Download and open example layout file in edb format.
edb_path = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb',
                                           destination=temp_dir.name)
edb = pyaedt.Edb(edb_path, edbversion="2023.2")

###############################################################################
# ## Cutout
#
# The ``Edb.cutout()`` method takes a list of
# signal nets as the first argument and a list of
# reference nets as the 2nd argument.
edb.cutout([signal_net_name], [coplanar_plane_net_name, "GND"],
              remove_single_pin_components=True)

###############################################################################
# Retrive the path segments from the signal net.
net = edb.nets[signal_net_name]
trace_segments = []
for p in net.primitives:
    if p.layer_name not in layers:
        continue
    if not p.type == "Path":
        continue
    trace_segments.append(p)

###############################################################################
# Create and assign delta w variable per layer.
for p in trace_segments:
    vname = f"{p.net_name}_{p.layer_name}_dw"
    if vname not in edb.variables:
        edb[vname] = "0mm"
    new_w = f"{p.width}+{vname}"
    p.width = new_w

###############################################################################
# Delete existing clearance.
for p in trace_segments:
    for g in edb.modeler.get_polygons_by_layer(p.layer_name, 
                                               coplanar_plane_net_name):
        for v in g.voids:
            if p.is_intersecting(v):
                v.delete()

###############################################################################
# Create and assign the clearance variable for each layer.
for p in trace_segments:
    clr = f"{p.net_name}_{p.layer_name}_clr"
    if clr not in edb.variables:
        edb[clr] = "0.5mm"
    path = p.get_center_line()
    for g in edb.modeler.get_polygons_by_layer(p.layer_name, 
                                               coplanar_plane_net_name):
        void = edb.modeler.create_trace(path, p.layer_name, f"{p.width}+{clr}*2")
        g.add_void(void)

###############################################################################
# Visualize the layout.
edb.nets.plot(layers=layers[0], size=2000)

###############################################################################
# Save and close the EDB.

save_edb_path = os.path.join(temp_dir.name, "post_layout_parameterization.aedb")
edb.save_edb_as(save_edb_path)
print("Edb is saved to ", save_edb_path)
edb.close_edb()

###############################################################################
# Clean up the temporary folder.

temp_dir.cleanup()
