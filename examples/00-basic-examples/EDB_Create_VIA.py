"""

Edb Parametric Via Creation
--------------------------------------------
This Example shows how to use EDB to create a Layout
"""
# sphinx_gallery_thumbnail_path = 'Resources/3dlayout.png'



#########################################
# Import Edb Layout object and initialize it on version 2021.1
#

import os
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name
if os.name == "posix":
    aedb_path = os.path.join("/tmp", generate_unique_name("Edb_custom") + ".aedb")
else:
    aedb_path=os.path.join(r"C:\Temp", generate_unique_name("Edb_custom")+".aedb")
edb = Edb(edbpath=aedb_path, edbversion="2021.1")


#########################################
# Create a stackup
#

edb.core_stackup.stackup_layers.add_layer("GND")
edb.core_stackup.stackup_layers.add_layer("Diel","GND", layerType=1, thickness="0.1mm", material="FR4_epoxy")
edb.core_stackup.stackup_layers.add_layer("TOP","Diel", thickness="0.05mm")
#########################################
# Create of signal net and ground planes
#
points = [
    [0.0, 0],
    [100e-3, 0.0],
]
path = edb.core_primitives.Shape('polygon', points=points)
edb.core_primitives.create_path(path, "TOP", width=1e-3)
points = [[0.0, 1e-3],[0.0, 10e-3], [100e-3, 10e-3],[100e-3, 1e-3],[0.0, 1e-3] ]
plane = edb.core_primitives.Shape('polygon', points=points)
edb.core_primitives.create_polygon(plane, "TOP")

points = [[0.0, -1e-3],[0.0, -10e-3], [100e-3, -10e-3],[100e-3, -1e-3],[0.0, -1e-3] ]
plane = edb.core_primitives.Shape('polygon', points=points)
edb.core_primitives.create_polygon(plane, "TOP")

#########################################
# Create of vias with parametric position
#

edb.core_padstack.create_padstack("MyVia")
edb.core_padstack.place_padstack([5e-3,5e-3], "MyVia")
edb.core_padstack.place_padstack([15e-3,5e-3], "MyVia")
edb.core_padstack.place_padstack([35e-3,5e-3], "MyVia")
edb.core_padstack.place_padstack([45e-3,5e-3], "MyVia")
edb.core_padstack.place_padstack([5e-3,-5e-3], "MyVia")
edb.core_padstack.place_padstack([15e-3,-5e-3], "MyVia")
edb.core_padstack.place_padstack([35e-3,-5e-3], "MyVia")
edb.core_padstack.place_padstack([45e-3,-5e-3], "MyVia")


#########################################
# Save and Close EDB
#
edb.save_edb()
edb.close_edb()
print("EDB Saved Correctly to {}. You can import in AEDT".format(aedb_path))