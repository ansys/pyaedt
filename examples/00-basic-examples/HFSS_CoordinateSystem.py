"""

Coordinate Sytems creation example
----------------------------------
This tutorial shows how you can use PyAedt to create and modify the coordinate systems in the modeler.
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

#####################################################
# Start Desktop in Graphical mode
# -------------------------------
# This examples will use AEDT 2021.1 in Graphical mode
d = Desktop("2021.1", non_graphical=False)

#####################################################
# Insert HFSS design
# ------------------
# This command insert an hfss design with a default name.
hfss = Hfss()

#####################################################
# Create a Coordinate System
# --------------------------
# The coordinate system is centered on Global origin and has the axis aligned to Global
# the coordinate system is saved in the object cs1
cs1 = hfss.modeler.create_coordinate_system()

#####################################################
# Edit the Coordinate System
# --------------------------
# The cs1 object expose properties and methods to manipulate the coordinate system.
# The origin can be changed
cs1.props["OriginX"] = 10
cs1.props["OriginY"] = 10
cs1.props["OriginZ"] = 10
cs1.update()

# The pointing vectors can be changed
ypoint = [0, -1, 0]
cs1.props["YAxisXvec"] = ypoint[0]
cs1.props["YAxisYvec"] = ypoint[1]
cs1.props["YAxisZvec"] = ypoint[2]
cs1.update()

#####################################################
# Rename the Coordinate System mode
# ---------------------------------
# The name can be changed
cs1.rename('newCS')

#####################################################
# Change the Coordinate System mode
# ---------------------------------
# Use the option to select the mode: 0 for "Axis/Position", 1 for "Euler Angle ZXZ", 2 for "Euler Angle ZYZ"
# This will change to "Euler Angle ZXZ"
cs1.change_cs_mode(1)

# With the new mode there are new properties that can be edited.
cs1.props["Phi"] = "10deg"
cs1.props["Theta"] = "22deg"
cs1.props["Psi"] = "30deg"
cs1.update()

#####################################################
# Delete the Coordinate System mode
# ---------------------------------
# The coordinate system can be deleted
cs1.delete()

#####################################################
# Create a new Coordinate System defining the axis
# ------------------------------------------------
# All the coordinate system properties can be specified at the creation
cs2 = hfss.modeler.create_coordinate_system(name='CS2',
                                            origin=[1, 2, 3.5],
                                            mode='axis',
                                            x_pointing=[1, 0, 1], y_pointing=[0, -1, 0])

#####################################################
# Create a new Coordinate System defining the Euler angles
# --------------------------------------------------------
# All the coordinate system properties can be specified at the creation.
# Here we specify the Euler angles
cs3 = hfss.modeler.create_coordinate_system(name='CS3',
                                            origin=[2, 2, 2],
                                            mode='zyz',
                                            phi=10, theta=20, psi=30)

#####################################################
# Create a new Coordinate System defining the view
# ------------------------------------------------
# A convenient creation option lets specify the view ( "iso", "XY", "XZ", "XY").
# The axis are set automatically
cs4 = hfss.modeler.create_coordinate_system(name='CS4',
                                            origin=[1, 0, 0],
                                            reference_cs='CS3',
                                            mode='view',
                                            view='iso')

#####################################################
# Create a new Coordinate System defining the axis/angle
# ------------------------------------------------------
# Axis/angle rotation can be also used. It is automatically translated in Euler angles.
cs5 = hfss.modeler.create_coordinate_system(name='CS5',
                                            mode='axisrotation',
                                            u=[1, 0, 0], theta=123)

#####################################################
# Get the Coordinate Systems
# --------------------------
# Coordinate Systems can be retrieved
css = hfss.modeler.coordinate_systems
names = [i.name for i in css]
print(names)

#####################################################
# Select a Coordinate system
# --------------------------
# select a previously created coordinate system
css = hfss.modeler.coordinate_systems
cs_selected = css[0]
cs_selected.delete()

#####################################################
# Get a point coordinate under another coordinate system
# ------------------------------------------------------
# A point coordinate can be translated respect any coordinate system
hfss.modeler.primitives.create_box([-10, -10, -10], [20, 20, 20], "Box1")
p = hfss.modeler.primitives['Box1'].faces[0].vertices[0].position
print('Global: ', p)
p2 = hfss.modeler.global_to_cs(p, 'CS5')
print('CS5 :', p2)

#####################################################
# Close Desktop
# -------------
if os.name != "posix":
    d.close_desktop()
