"""
Coordinate System Creation Example
----------------------------------
This example shows how you can use PyAEDT to create and modify coordinate systems in the modeler.
"""
# sphinx_gallery_thumbnail_path = 'Resources/coordinate_system.png'

import os
from pyaedt import Hfss
from pyaedt import Desktop
from pyaedt import generate_unique_name
if os.name == "posix":
    tmpfold= os.environ["TMPDIR"]
else:
    tmpfold= os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

###############################################################################
# Launch AEDT in graphical mode.
# ------------------------------
# This example launches AEDT 2021.1 in graphical mode.

nongraphical = False
d = Desktop("2021.1", NG=nongraphical)

###############################################################################
# Insert an HFSS design.
# ----------------------
# This command inserts an HFSS design with the default name.
hfss = Hfss()

###############################################################################
# Create a coordinate system.
# ---------------------------
# The coordinate system is centered on the ``Global`` origin and has the axis 
# aligned to the ``Global`` coordinate system.
# The new coordinate system is saved in the object `cs1`.

cs1 = hfss.modeler.create_coordinate_system()

###############################################################################
# Modify the coordinate system.
# -----------------------------
# The `cs1` object exposes properties and methods to manipulate the coordinate system.
# The origin can be changed.

cs1.props["OriginX"] = 10
cs1.props["OriginY"] = 10
cs1.props["OriginZ"] = 10
cs1.update()

# The pointing vectors can be changed.

ypoint = [0, -1, 0]
cs1.props["YAxisXvec"] = ypoint[0]
cs1.props["YAxisYvec"] = ypoint[1]
cs1.props["YAxisZvec"] = ypoint[2]
cs1.update()

###############################################################################
# Rename the coordinate system.
# -----------------------------

cs1.rename('newCS')

###############################################################################
# Change the coordinate system mode.
# ----------------------------------
# Use the function `change_cs_mode` to change the mode: ``0`` for "Axis/Position", 
# ``1`` for "Euler Angle ZXZ", or ``2`` for "Euler Angle ZYZ".
# This command changes the mode to "Euler Angle ZXZ".

cs1.change_cs_mode(1)

# In the new mode, there are properties that can be edited.

cs1.props["Phi"] = "10deg"
cs1.props["Theta"] = "22deg"
cs1.props["Psi"] = "30deg"
cs1.update()

###############################################################################
# Delete the coordinate system.
# -----------------------------

cs1.delete()

###############################################################################
# Create a coordinate system, defining the axes.
# ----------------------------------------------
# All coordinate system properties can be specified at the creation.
# Here the axes are specified.

cs2 = hfss.modeler.create_coordinate_system(name='CS2',
                                            origin=[1, 2, 3.5],
                                            mode='axis',
                                            x_pointing=[1, 0, 1], y_pointing=[0, -1, 0])

###############################################################################
# Create a coordinate system defining the Euler angles.
# -----------------------------------------------------
# All coordinate system properties can be specified at the creation.
# Here Euler angles are specified.

cs3 = hfss.modeler.create_coordinate_system(name='CS3',
                                            origin=[2, 2, 2],
                                            mode='zyz',
                                            phi=10, theta=20, psi=30)

###############################################################################
# Create a coordinate system defining the view.
# ---------------------------------------------
# Any of these views can be specified: ``"iso"``, ``"XY"``, ``"XZ"``, or ``"XY"``.
# Here the ``"iso"` view is specified.
# The axes are set automatically.

cs4 = hfss.modeler.create_coordinate_system(name='CS4',
                                            origin=[1, 0, 0],
                                            reference_cs='CS3',
                                            mode='view',
                                            view='iso')

###############################################################################
# Create a coordinate system defining the axis and angle rotation.
# ----------------------------------------------------------------
# When the axis and angle rotation are specified, this data is automatically 
# translated to Euler angles.

cs5 = hfss.modeler.create_coordinate_system(name='CS5',
                                            mode='axisrotation',
                                            u=[1, 0, 0], theta=123)

###############################################################################
# Get all coordinate systems.
# ---------------------------

css = hfss.modeler.coordinate_systems
names = [i.name for i in css]
print(names)

###############################################################################
# Select a coordinate system.
# ---------------------------
# select a previously created coordinate system
css = hfss.modeler.coordinate_systems
cs_selected = css[0]
cs_selected.delete()

###############################################################################
# Get a point coordinate under another coordinate system.
# -------------------------------------------------------
# A point coordinate can be translated in respect to any coordinate system.

hfss.modeler.primitives.create_box([-10, -10, -10], [20, 20, 20], "Box1")
p = hfss.modeler.primitives['Box1'].faces[0].vertices[0].position
print('Global: ', p)
p2 = hfss.modeler.global_to_cs(p, 'CS5')
print('CS5 :', p2)

###############################################################################
# Close AEDT.
# -----------
if os.name != "posix":
    d.close_desktop()
