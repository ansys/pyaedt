"""
Edb: Fully parameterized design
-------------------------------
This example shows how to use HFSS 3D Layout to create and solve a parametric design.
"""

###############################################################################
# Import the `Hfss3dlayout` Object
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example imports the `Hfss3dlayout` object and initializes it on version
# 2022.1.

import tempfile
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt import Hfss3dLayout
import os

tmpfold = tempfile.gettempdir()
aedb_path = os.path.join(tmpfold, generate_unique_name("pcb") + ".aedb")
print(aedb_path)
edb = Edb(edbpath=aedb_path, edbversion="2022.1")
var_server = edb.active_cell.GetVariableServer()


class via_def:
    def __init__(
        self,
        name="via_def",
        hole_diam="",
        pad_diam="",
        anti_pad_diam="",
        start_layer="top",
        stop_layer="bottom",
        antipad_shape="Circle",
        x_size="",
        y_size="",
        corner_rad="",
    ):
        self.name = name
        self.hole_diam = hole_diam
        self.pad_diam = pad_diam
        self.anti_pad_diam = anti_pad_diam
        self.start_layer = start_layer
        self.stop_layer = stop_layer
        self.anti_pad_shape = antipad_shape
        self.x_size = x_size
        self.y_size = y_size
        self.corner_rad = corner_rad

    def add_via_def_to_edb(self):
        edb.core_padstack.create_padstack(
            padstackname=self.name,
            holediam=self.hole_diam,
            paddiam=self.pad_diam,
            antipaddiam=self.anti_pad_diam,
            startlayer=self.start_layer,
            endlayer=self.stop_layer,
            antipad_shape=self.anti_pad_shape,
            x_size=self.x_size,
            y_size=self.y_size,
            corner_radius=self.corner_rad,
        )


class via_instance:
    def __init__(self, pos_x="", pos_y="", rotation=0.0, net_name=""):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rotation = rotation
        self.pos = [self.pos_x, self.pos_y]
        self.net_name = net_name

    def place_via(self, viadef=via_def()):
        edb_padstanck_inst = edb.core_padstack.place_padstack(
            position=self.pos,
            definition_name=viadef.name,
            net_name=self.net_name,
            via_name="",
            rotation=self.rotation,
            fromlayer=viadef.start_layer,
            tolayer=viadef.stop_layer,
        )


class line:
    def __init__(self, width="0.0", point_list=None, layer="", net_name=""):
        if point_list is None:
            point_list = [[0.0, 0.0], [1e-3, 0.0]]
        self.point_list = point_list
        self.width = width
        self.layer = layer
        self.net_name = net_name

    def place_line(self):
        path = edb.core_primitives.Shape("polygon", points=self.point_list)
        edb_path = edb.core_primitives.create_path(
            path, self.layer, self.width, self.net_name, start_cap_style="Flat", end_cap_style="Flat"
        )
        return edb_path


class rectangle:
    def __init__(self, lower_left_corner=[], upper_right_corner=[], voids=None):
        self.lower_left_corner = lower_left_corner
        self.upper_right_corner = upper_right_corner
        self.voids = voids

    def place_rectangle(self, layer_name="top", net_name=""):
        pts = [
            [self.lower_left_corner[0], self.lower_left_corner[1]],
            [self.upper_right_corner[0], self.lower_left_corner[1]],
            [self.upper_right_corner[0], self.upper_right_corner[1]],
            [self.lower_left_corner[0], self.upper_right_corner[1]],
        ]
        shape = edb.core_primitives.Shape("polygon", points=pts)
        if self.voids:
            shape_void = [edb.core_primitives.Shape("polygon", points=self.voids)]
        else:
            shape_void = []
        edb.core_primitives.create_polygon(main_shape=shape, layer_name=layer_name, voids=shape_void, net_name=net_name)

    def get_variable_value(self, variable_name=""):
        value = edb.edb_value()
        var_value = var_server.get_variable_value(variable_name, value)
        return value.ToDouble()


####################
# Layer stackup
#
if edb:
    edb.core_stackup.stackup_layers.add_layer("bottom")
    edb.core_stackup.stackup_layers.add_layer(
        "dielectric", "bottom", layerType=1, thickness="275um", material="FR4_epoxy"
    )
    edb.core_stackup.stackup_layers.add_layer("sig2", "dielectric")
    edb.core_stackup.stackup_layers.add_layer("Diel_2", "sig2", layerType=1, thickness="275um", material="FR4_epoxy")
    edb.core_stackup.stackup_layers.add_layer("sig1", "Diel_2")
    edb.core_stackup.stackup_layers.add_layer("Diel_1", "sig1", layerType=1, thickness="275um", material="FR4_epoxy")
    edb.core_stackup.stackup_layers.add_layer("top", "Diel_1")

####################
# Design variables
#
edb.add_design_variable("$line_width", "0.5mm")
edb.add_design_variable("$line2_width", "0.5mm")
edb.add_design_variable("$line_spacing", "0.2mm")
edb.add_design_variable("$via_spacing", "0.5mm")
edb.add_design_variable("$via_diam", "0.3mm")
edb.add_design_variable("$pad_diam", "0.6mm")
edb.add_design_variable("$anti_pad_diam", "0.7mm")
edb.add_design_variable("$pcb_len", "30mm")
edb.add_design_variable("$pcb_w", "5mm")
edb.add_design_variable("$x_size", "1.2mm")
edb.add_design_variable("$y_size", "1mm")
edb.add_design_variable("$corner_rad", "0.5mm")

#################
# Via definition
#
viadef1 = via_def(
    name="automated_via",
    hole_diam="$via_diam",
    pad_diam="$pad_diam",
    antipad_shape="Bullet",
    x_size="$x_size",
    y_size="$y_size",
    corner_rad="$corner_rad",
)
viadef1.add_via_def_to_edb()

###################
# line creation
#
net_name = "strip_line_p"
net_name2 = "strip_line_n"

######################
# line placement
#
seg1_p = line(width="$line_width", net_name=net_name, layer="top")

seg1_p.point_list = [
    ["0.0", "($line_width+$line_spacing)/2"],
    ["$pcb_len/3-2*$via_spacing", "($line_width+$line_spacing)/2"],
    ["$pcb_len/3-$via_spacing", "($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3", "($line_width+$line_spacing+$via_spacing)/2"],
]
seg1_p.place_line()
path_port_1p = edb.core_primitives.primitives[-1]

####################
# via placement
#

via_instance(
    pos_x="$pcb_len/3", pos_y="($line_width+$line_spacing+$via_spacing)/2", rotation=90, net_name=net_name
).place_via(viadef1)

####################
# line creation
#
seg2_p = line(width="$line2_width", net_name=net_name, layer="sig1")
seg2_p.point_list = [
    ["$pcb_len/3", "($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3+$via_spacing", "($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3+2*$via_spacing", "($line_width+$line_spacing)/2"],
    ["2*$pcb_len/3-2*$via_spacing", "($line_width+$line_spacing)/2"],
    ["2*$pcb_len/3-$via_spacing", "($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3", "($line_width+$line_spacing+$via_spacing)/2"],
]
seg2_p.place_line()

##################
# Via placement
#
via_instance(
    pos_x="2*$pcb_len/3", pos_y="($line_width+$line_spacing+$via_spacing)/2", rotation=90, net_name=net_name
).place_via(viadef1)

####################
# line creation
#

seg3_p = line(width="$line_width", net_name=net_name, layer="top")
seg3_p.point_list = [
    ["2*$pcb_len/3", "($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3+$via_spacing", "($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3+2*$via_spacing", "($line_width+$line_spacing)/2"],
    ["$pcb_len", "($line_width+$line_spacing)/2"],
]
seg3_p.place_line()
path_port_2p = edb.core_primitives.primitives[-1]

##################
# line n
#
# line creation
seg1_n = line(width="$line_width", net_name=net_name2, layer="top")

seg1_n.point_list = [
    ["0.0", "-($line_width+$line_spacing)/2"],
    ["$pcb_len/3-2*$via_spacing", "-($line_width+$line_spacing)/2"],
    ["$pcb_len/3-$via_spacing", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3", "-($line_width+$line_spacing+$via_spacing)/2"],
]
seg1_n.place_line()

##################
# via placement
#

via_instance(
    pos_x="$pcb_len/3", pos_y="-($line_width+$line_spacing+$via_spacing)/2", rotation=-90, net_name=net_name2
).place_via(viadef1)

##################
# line creation
#

seg2_n = line(width="$line2_width", net_name=net_name2, layer="sig1")
seg2_n.point_list = [
    ["$pcb_len/3", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3+$via_spacing", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["$pcb_len/3+2*$via_spacing", "-($line_width+$line_spacing)/2"],
    ["2*$pcb_len/3-2*$via_spacing", "-($line_width+$line_spacing)/2"],
    ["2*$pcb_len/3-$via_spacing", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3", "-($line_width+$line_spacing+$via_spacing)/2"],
]
seg2_n.place_line()

##################
# via placement
#

via_instance(
    pos_x="2*$pcb_len/3", pos_y="-($line_width+$line_spacing+$via_spacing)/2", rotation=-90, net_name=net_name2
).place_via(viadef1)

####################
# line creation

seg3_p = line(width="$line_width", net_name=net_name2, layer="top")
seg3_p.point_list = [
    ["2*$pcb_len/3", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3+$via_spacing", "-($line_width+$line_spacing+$via_spacing)/2"],
    ["2*$pcb_len/3+2*$via_spacing", "-($line_width+$line_spacing)/2"],
    ["$pcb_len", "-($line_width+$line_spacing)/2"],
]
seg3_p.place_line()
##########################
# GND plane
#

rectangle(
    lower_left_corner=[0.0, "-$pcb_w/2"],
    upper_right_corner=["$pcb_len", "$pcb_w/2"],
    voids=[
        ["$pcb_len/3", "-($line_width+$line_spacing+$via_spacing+$anti_pad_diam)/2"],
        ["2*$pcb_len/3", "-($line_width+$line_spacing+$via_spacing+$anti_pad_diam)/2"],
        ["2*$pcb_len/3", "($line_width+$line_spacing+$via_spacing+$anti_pad_diam)/2"],
        ["$pcb_len/3", "($line_width+$line_spacing+$via_spacing+$anti_pad_diam)/2"],
    ],
).place_rectangle("sig1", "gnd")

gnd_plane = edb.core_primitives.primitives[-1]
#
rectangle(lower_left_corner=[0.0, "-$pcb_w/2"], upper_right_corner=["$pcb_len", "$pcb_w/2"]).place_rectangle(
    "sig2", "gnd"
)

rectangle(lower_left_corner=[0.0, "-$pcb_w/2"], upper_right_corner=["$pcb_len", "$pcb_w/2"]).place_rectangle(
    "bottom", "gnd"
)

##########################
# Plotting the Edb
edb.core_nets.plot(None)
##########################
# saving edb
edb.save_edb()
edb.close_edb()

##########################
# opening edb in aedt
h3d = Hfss3dLayout(projectname=os.path.join(aedb_path, "edb.def"), specified_version="2022.1", non_graphical=False)

##########################
# creating wave ports

h3d.create_wave_port_from_two_conductors(["line_0", "line_3"], [0, 0])
h3d.create_wave_port_from_two_conductors(["line_5", "line_2"], [5, 5])

##########################
# adding hfss simulation setup

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

##########################
# start hfss solver. Uncomment to solve
# h3d.analyze_nominal()
h3d.release_desktop()
