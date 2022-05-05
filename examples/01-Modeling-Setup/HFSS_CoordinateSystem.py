"""
General: Coordinate System Creation
-----------------------------------
This example shows how you can use PyAEDT to create and modify coordinate systems in the modeler.
"""
# sphinx_gallery_thumbnail_path = 'Resources/coordinate_system.png'

import os
import tempfile

from pyaedt import Hfss
from pyaedt import Desktop
from pyaedt import generate_unique_name

tmpfold = tempfile.gettempdir()

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

###############################################################################
# Launch AEDT in Graphical Mode
# -----------------------------
# This example launches AEDT 2022R1 in graphical mode.

nongraphical = False
d = Desktop("2022.1", non_graphical=nongraphical, new_desktop_session=True)

###############################################################################
# Insert an HFSS Design
# ---------------------
# This command inserts an HFSS design with the default name.
hfss = Hfss()

###############################################################################
# Create a Coordinate System
# --------------------------
# The coordinate system is centered on the ``Global`` origin and has the axis
# aligned to the ``Global`` coordinate system.
# The new coordinate system is saved in the object `cs1`.

cs1 = hfss.modeler.create_coordinate_system()

###############################################################################
# Modify the Coordinate System
# ----------------------------
# The `cs1` object exposes properties and methods to manipulate the coordinate system.
# The origin can be changed.

cs1.props["OriginX"] = 10
cs1.props["OriginY"] = 10
cs1.props["OriginZ"] = 10

# The pointing vectors can be changed.

ypoint = [0, -1, 0]
cs1.props["YAxisXvec"] = ypoint[0]
cs1.props["YAxisYvec"] = ypoint[1]
cs1.props["YAxisZvec"] = ypoint[2]

###############################################################################
# Rename the Coordinate System
# ----------------------------
# This command renames the coordinate system.

cs1.rename("newCS")

###############################################################################
# Change the Coordinate System Mode
# ---------------------------------
# Use the function `change_cs_mode` to change the mode: ``0`` for "Axis/Position",
# ``1`` for "Euler Angle ZXZ", or ``2`` for "Euler Angle ZYZ".
# This command changes the mode to "Euler Angle ZXZ".

cs1.change_cs_mode(1)

# In the new mode, there are properties that can be edited.
cs1.props["Phi"] = "10deg"
cs1.props["Theta"] = "22deg"
cs1.props["Psi"] = "30deg"

###############################################################################
# Delete the Coordinate System
# ----------------------------
# This command deletes the coordinate system.

cs1.delete()

###############################################################################
# Create a Coordinate System by Defining Axes
# -------------------------------------------
# All coordinate system properties can be specified at the creation.
# Here the axes are specified.

cs2 = hfss.modeler.create_coordinate_system(
    name="CS2", origin=[1, 2, 3.5], mode="axis", x_pointing=[1, 0, 1], y_pointing=[0, -1, 0]
)

###############################################################################
# Create a Coordinate System by Defining Euler Angles
# ---------------------------------------------------
# Here Euler angles are specified.

cs3 = hfss.modeler.create_coordinate_system(name="CS3", origin=[2, 2, 2], mode="zyz", phi=10, theta=20, psi=30)

###############################################################################
# Create a Coordinate System by Defining the View
# -----------------------------------------------
# Any of these views can be specified: ``"iso"``, ``"XY"``, ``"XZ"``, or ``"XY"``.
# Here the ``"iso"`` view is specified.
# The axes are set automatically.

cs4 = hfss.modeler.create_coordinate_system(name="CS4", origin=[1, 0, 0], reference_cs="CS3", mode="view", view="iso")

###############################################################################
# Create a Coordinate System by Defining the Axis and Angle Rotation
# -------------------------------------------------------------------
# When the axis and angle rotation are specified, this data is automatically
# translated to Euler angles.

cs5 = hfss.modeler.create_coordinate_system(name="CS5", mode="axisrotation", u=[1, 0, 0], theta=123)

###############################################################################
# Create a Face Coordinate System
# -------------------------------
# Face coordinate systems are bound to an object face.
# Here we create first a box and then a Face Coordinate System is defined on one of its faces.
# To create the face coordinate system a reference face, the axis starting and ending points must be specified.
box = hfss.modeler.create_box([0, 0, 0], [2, 2, 2])
face = box.faces[0]
fcs1 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face.edges[0], axis_position=face.edges[1], name="FCS1"
)

###############################################################################
# Create a Face Coordinate System centered on the face
# ----------------------------------------------------
# Here we create a Face Coordinate System centered on the face and with the X axis pointing to the edge vertex.
fcs2 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[0].vertices[0], name="FCS2"
)

###############################################################################
# Swap the X and Y axis of a Face coordinate system
# -------------------------------------------------
# As default the X axis is pointing `axis_position`. Optionally the Y axis can be selected.
fcs3 = hfss.modeler.create_face_coordinate_system(face=face, origin=face, axis_position=face.edges[0], axis="Y")

# The axis can also be changed after the coordinate system is created.
fcs3.props["WhichAxis"] = "X"

###############################################################################
# Apply a rotation around the Z axis
# ----------------------------------
# The Z axis of a Face Coordinate System is always orthogonal to the face.
# A rotation can be applied at definition. The rotation is expressed in degrees.
fcs4 = hfss.modeler.create_face_coordinate_system(face=face, origin=face, axis_position=face.edges[1], rotation=10.3)

# The rotation can also be changed after the coordinate system is created.
fcs4.props["ZRotationAngle"] = "3deg"

###############################################################################
# Apply an offset to the X and Y axis of a Face coordinate system
# ---------------------------------------------------------------
# The offset is respect the Face Coordinate System itself.
fcs5 = hfss.modeler.create_face_coordinate_system(
    face=face, origin=face, axis_position=face.edges[2], offset=[0.5, 0.3]
)

# The offset can also be changed after the coordinate system is created.
fcs5.props["XOffset"] = "0.2mm"
fcs5.props["YOffset"] = "0.1mm"

###############################################################################
# Create a coordinate system relative to a Face coordinate system
# ---------------------------------------------------------------
# Coordinate Systems and Face Coordinate Systems interact each other.
face = box.faces[1]
fcs6 = hfss.modeler.create_face_coordinate_system(face=face, origin=face, axis_position=face.edges[0])
cs_fcs = hfss.modeler.create_coordinate_system(
    name="CS_FCS", origin=[0, 0, 0], reference_cs=fcs6.name, mode="view", view="iso"
)


###############################################################################
# Get All Coordinate Systems
# --------------------------
# This example gets all coordinate systems.

css = hfss.modeler.coordinate_systems
names = [i.name for i in css]
print(names)

###############################################################################
# Select a Coordinate System
# --------------------------
# This example selects an existing coordinate system.

css = hfss.modeler.coordinate_systems
cs_selected = css[0]
cs_selected.delete()

###############################################################################
# Get a Point Coordinate Under Another Coordinate System
# ------------------------------------------------------
# A point coordinate can be translated in respect to any coordinate system.

hfss.modeler.create_box([-10, -10, -10], [20, 20, 20], "Box1")
p = hfss.modeler["Box1"].faces[0].vertices[0].position
print("Global: ", p)
p2 = hfss.modeler.global_to_cs(p, "CS5")
print("CS5 :", p2)

###############################################################################
# Close AEDT
# ----------
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.

if os.name != "posix":
    d.release_desktop()
