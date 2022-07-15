"""
EDB: geometry creation
----------------------
This example shows how to use EDB to create a layout.
"""

##########################
# Import EDB layout object
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Import the EDB layout object and initialize it on version 2022 R2.

import time
import os
import tempfile
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name

start = time.time()

tmpfold = tempfile.gettempdir()
aedb_path = os.path.join(tmpfold, generate_unique_name("pcb") + ".aedb")
print(aedb_path)
edb = Edb(edbpath=aedb_path, edbversion="2022.2")

####################
# Add stackup layers
# ~~~~~~~~~~~~~~~~~~
# Add stackup layers.
#
if edb:
    edb.core_stackup.stackup_layers.add_layer("GND")
    edb.core_stackup.stackup_layers.add_layer("Diel", "GND", layerType=1, thickness="0.1mm", material="FR4_epoxy")
    edb.core_stackup.stackup_layers.add_layer("TOP", "Diel", thickness="0.05mm")

#####################################
# Create signal net and ground planes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a signal net and ground planes.

if edb:
    points = [
        [0.0, 0],
        [100e-3, 0.0],
    ]
    path = edb.core_primitives.Shape("polygon", points=points)
    edb.core_primitives.create_path(path, "TOP", width=1e-3)
    points = [[0.0, 1e-3], [0.0, 10e-3], [100e-3, 10e-3], [100e-3, 1e-3], [0.0, 1e-3]]
    plane = edb.core_primitives.Shape("polygon", points=points)
    edb.core_primitives.create_polygon(plane, "TOP")

    points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
    plane = edb.core_primitives.Shape("polygon", points=points)
    edb.core_primitives.create_polygon(plane, "TOP")

#######################################
# Create vias with parametric positions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create vias with parametric positions.

if edb:
    edb.core_padstack.create_padstack("MyVia")
    edb.core_padstack.place_padstack([5e-3, 5e-3], "MyVia")
    edb.core_padstack.place_padstack([15e-3, 5e-3], "MyVia")
    edb.core_padstack.place_padstack([35e-3, 5e-3], "MyVia")
    edb.core_padstack.place_padstack([45e-3, 5e-3], "MyVia")
    edb.core_padstack.place_padstack([5e-3, -5e-3], "MyVia")
    edb.core_padstack.place_padstack([15e-3, -5e-3], "MyVia")
    edb.core_padstack.place_padstack([35e-3, -5e-3], "MyVia")
    edb.core_padstack.place_padstack([45e-3, -5e-3], "MyVia")

edb.core_nets.plot(None)

####################
# Save and close EDB
# ~~~~~~~~~~~~~~~~~~
# Save and close EDB.

if edb:
    edb.save_edb()
    edb.close_edb()
print("EDB saved correctly to {}. You can import in AEDT.".format(aedb_path))
end = time.time() - start
print(end)
