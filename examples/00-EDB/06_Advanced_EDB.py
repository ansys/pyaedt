"""
EDB: parametric via creation
----------------------------
This example shows how to use EDB to create a layout.
"""
# sphinx_gallery_thumbnail_path = 'Resources/viawizard.png'

import os
import numpy as np
import tempfile
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name

tmpfold = tempfile.gettempdir()
if not os.path.exists(tmpfold):
    os.mkdir(tmpfold)
aedb_path = os.path.join(tmpfold, generate_unique_name("via_opt") + ".aedb")

###############################################################################
# Create stackup
# ~~~~~~~~~~~~~~
# The ``StackupSimple`` class creates a stackup based on few inputs. It is used later.

class StackupSimple:
    """Creates a typical PCB stackup"""

    def __init__(
        self,
        _edb,
        layer_count,
        diel_material_name="FR4_epoxy",
        diel_thickness="0.15mm",
        cond_thickness_outer="0.05mm",
        cond_thickness_inner="0.017mm",
        soldermask_thickness="0.05mm",
    ):
        """

        Parameters
        ----------
        _edb : Edb
        layer_count : int
            The number of stackup layers
        diel_material_name : str
            The name of the dielectric material defined in material library
        diel_thickness : str
            Thickess os all dielectric layers
        cond_thickness_outer : str
            Outer layer conductor thickness
        cond_thickness_inner : str
            Inner layour conductor thickness
        soldermask_thickness : str
            Soldermask thickness
        """
        self._edb = _edb
        self.layer_count = layer_count
        self.diel_material_name = diel_material_name
        self.diel_thickness = diel_thickness
        self.cond_thickness_outer = cond_thickness_outer
        self.cond_thickness_inner = cond_thickness_inner
        self.soldermask_thickness = soldermask_thickness

    def create_stackup(self):
        self._create_stackup_layer_list()
        self._edb_create_stackup()

    def _create_stackup_layer_list(self):
        self.stackup_list = []

        # Create top soldermask layer
        smt = {"layer_type": 1, "layer_name": "SMT", "material": "SolderMask", "thickness": self.soldermask_thickness}
        self.stackup_list.append(smt)

        for i in np.arange(1, self.layer_count + 1):

            # Create conductor layer
            fill_material = self.diel_material_name

            if i in [1, self.layer_count]:
                thickness = self.cond_thickness_outer
                fill_material = "SolderMask"
            else:
                thickness = self.cond_thickness_inner

            cond_layer = {
                "layer_type": 0,
                "layer_name": "L{}".format(str(i)),
                "fill_material": fill_material,
                "thickness": thickness,
            }
            self.stackup_list.append(cond_layer)

            # Check if it is the last conductor layer
            if i == self.layer_count:
                break

            # Create dielectric layer
            diel_material = self.diel_material_name
            diel_thickness = self.diel_thickness

            dielectric_layer = {
                "layer_type": 1,
                "layer_name": "D{}".format(str(i)),
                "material": diel_material,
                "thickness": diel_thickness,
            }
            self.stackup_list.append(dielectric_layer)

        # Create bottom soldermask layer
        smb = {"layer_type": 1, "layer_name": "SMB", "material": "SolderMask", "thickness": self.soldermask_thickness}
        self.stackup_list.append(smb)

    def _edb_create_stackup(self):
        base_layer = None
        while len(self.stackup_list):

            layer = self.stackup_list.pop(-1)
            if layer["layer_type"] == 1:

                self._edb.core_stackup.stackup_layers.add_layer(
                    layerName=layer["layer_name"],
                    start_layer=base_layer,
                    material=layer["material"],
                    thickness=layer["thickness"],
                    layerType=1,
                )
                base_layer = layer["layer_name"]
            else:

                self._edb.core_stackup.stackup_layers.add_layer(
                    layerName=layer["layer_name"],
                    start_layer=base_layer,
                    material="copper",
                    fillMaterial=layer["fill_material"],
                    thickness=layer["thickness"],
                    layerType=0,
                )
                base_layer = layer["layer_name"]


###############################################################################
# Create ground plane
# ~~~~~~~~~~~~~~~~~~~
# Create a ground plane on specific layers.

def _create_ground_planes(edb, layers):
    plane = edb.core_primitives.Shape("rectangle", pointA=["-3mm", "-3mm"], pointB=["3mm", "3mm"])
    for i in layers:
        edb.core_primitives.create_polygon(plane, i, net_name="GND")


##################################################################################
# Create EDB
# ~~~~~~~~~~
# Create EDB. If the path doesn't exist, PyAEDT automatically generates a new AEDB folder.

edb = Edb(edbpath=aedb_path, edbversion="2022.2")

##################################################################################
# Create stackup layers
# ~~~~~~~~~~~~~~~~~~~~~
# Create stackup layers.

layout_count = 12
diel_material_name = "FR4_epoxy"
diel_thickness = "0.15mm"
cond_thickness_outer = "0.05mm"
cond_thickness_inner = "0.017mm"
soldermask_thickness = "0.05mm"
trace_in_layer = "L1"
trace_out_layer = "L10"
gvia_num = 10
gvia_angle = 30

StackupSimple(
    edb,
    layer_count=layout_count,
    diel_material_name=diel_material_name,
    diel_thickness=diel_thickness,
    cond_thickness_outer=cond_thickness_outer,
    cond_thickness_inner=cond_thickness_inner,
    soldermask_thickness=soldermask_thickness,
).create_stackup()

##################################################################################
# Create parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create all variables. If a variable has a ``$`` prefix, it is a project variable.
# Otherwise, is is a design variable.

giva_angle_rad = gvia_angle / 180 * np.pi

edb.add_design_variable("$via_hole_size", "0.3mm")
edb.add_design_variable("$antipaddiam", "0.7mm")
edb.add_design_variable("$paddiam", "0.5mm")
edb.add_design_variable("via_pitch", "1mm", is_parameter=True)
edb.add_design_variable("trace_in_width", "0.2mm", is_parameter=True)
edb.add_design_variable("trace_out_width", "0.1mm", is_parameter=True)

##################################################################################
# Create padstacks
# ~~~~~~~~~~~~~~~~
# Create two padstacks, one for the ground and one for the signal. The padstacks
# are parametric.

edb.core_padstack.create_padstack(
    padstackname="SVIA", holediam="$via_hole_size", antipaddiam="$antipaddiam", paddiam="$paddiam"
)
edb.core_padstack.create_padstack(padstackname="GVIA", holediam="0.3mm", antipaddiam="0.7mm", paddiam="0.5mm")

##################################################################################
# Place padstack for signal
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Place the padstack for the signal.

edb.core_padstack.place_padstack([0, 0], "SVIA", net_name="RF", fromlayer=trace_in_layer, tolayer=trace_out_layer)

##################################################################################
# Place padstack for ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Place the padstack for the  ground. A loop iterates and places multiple ground
# vias on different positions.

gvia_num_side = gvia_num / 2

if gvia_num_side % 2:

    # Even number of ground vias on each side
    edb.core_padstack.place_padstack(["via_pitch", 0], "GVIA", net_name="GND")
    edb.core_padstack.place_padstack(["via_pitch*-1", 0], "GVIA", net_name="GND")
    for i in np.arange(1, gvia_num_side / 2):
        xloc = "{}*{}".format(np.cos(giva_angle_rad * i), "via_pitch")
        yloc = "{}*{}".format(np.sin(giva_angle_rad * i), "via_pitch")
        edb.core_padstack.place_padstack([xloc, yloc], "GVIA", net_name="GND")
        edb.core_padstack.place_padstack([xloc, yloc + "*-1"], "GVIA", net_name="GND")

        edb.core_padstack.place_padstack([xloc + "*-1", yloc], "GVIA", net_name="GND")
        edb.core_padstack.place_padstack([xloc + "*-1", yloc + "*-1"], "GVIA", net_name="GND")
else:

    # Odd number of ground vias on each side
    for i in np.arange(0, gvia_num_side / 2):
        xloc = "{}*{}".format(np.cos(giva_angle_rad * (i + 0.5)), "via_pitch")
        yloc = "{}*{}".format(np.sin(giva_angle_rad * (i + 0.5)), "via_pitch")
        edb.core_padstack.place_padstack([xloc, yloc], "GVIA", net_name="GND")
        edb.core_padstack.place_padstack([xloc, yloc + "*-1"], "GVIA", net_name="GND")

        edb.core_padstack.place_padstack([xloc + "*-1", yloc], "GVIA", net_name="GND")
        edb.core_padstack.place_padstack([xloc + "*-1", yloc + "*-1"], "GVIA", net_name="GND")

##################################################################################
# Generate traces
# ~~~~~~~~~~~~~~~
# Generate and place parametric traces.

path = edb.core_primitives.Shape("polygon", points=[[0, 0], [0, "-3mm"]])
edb.core_primitives.create_path(
    path, layer_name=trace_in_layer, net_name="RF", width="trace_in_width", start_cap_style="Flat", end_cap_style="Flat"
)

path = edb.core_primitives.Shape("polygon", points=[[0, 0], [0, "3mm"]])
edb.core_primitives.create_path(
    path,
    layer_name=trace_out_layer,
    net_name="RF",
    width="trace_out_width",
    start_cap_style="Flat",
    end_cap_style="Flat",
)

##################################################################################
# Generate ground layers
# ~~~~~~~~~~~~~~~~~~~~~~
# Geneerate and place ground layers.

ground_layers = ["L" + str(i + 1) for i in np.arange(layout_count)]
ground_layers.remove(trace_in_layer)
ground_layers.remove(trace_out_layer)
_create_ground_planes(edb=edb, layers=ground_layers)

##################################################################################
# Save EDB and close
# ~~~~~~~~~~~~~~~~~~
# Save EDB and close.

edb.save_edb()
edb.close_edb()

print("aedb Saved in {}".format(aedb_path))
