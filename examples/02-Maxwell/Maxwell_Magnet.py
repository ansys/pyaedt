"""
Maxwell 3d: Magnet DC Analysis
------------------------------
This example shows how you can use PyAEDT to create a Maxwell DC Analysis,
compute mass center and move Coordinate Systems.
"""

from pyaedt import Maxwell3d
import os
import tempfile

tmpfold = tempfile.gettempdir()
if not os.path.exists(tmpfold):
    os.mkdir(tmpfold)

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2022R1 in graphical mode.
m3d = Maxwell3d(specified_version="2022.1", new_desktop_session=True)


###############################################################################
# Setup Maxwell Solution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setup Maxwell Solution to DC.
m3d.solution_type = m3d.SOLUTIONS.Maxwell3d.ElectroDCConduction


###############################################################################
# Create Magnet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

magnet = m3d.modeler.create_box([7, 4, 22], [10, 5, 30], name="Magnet", matname="copper")


###############################################################################
# Create Setup and Assign Voltage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
m3d.assign_voltage(magnet.faces, 0)
m3d.create_setup()


###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

m3d.plot(show=False, export_path=os.path.join(m3d.working_directory, "Image.jpg"), plot_air_objects=True)

###############################################################################
# Solve Setup
# ~~~~~~~~~~~
m3d.analyze_nominal()


###############################################################################
# Compute Mass Center
# ~~~~~~~~~~~~~~~~~~~~~
# Field Calculator is used to compute mass center.

m3d.post.ofieldsreporter.EnterScalarFunc("X")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_X", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Y")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Y", "Fields")
m3d.post.ofieldsreporter.EnterScalarFunc("Z")
m3d.post.ofieldsreporter.EnterVol(magnet.name)
m3d.post.ofieldsreporter.CalcOp("Mean")
m3d.post.ofieldsreporter.AddNamedExpression("CM_Z", "Fields")
m3d.post.ofieldsreporter.CalcStack("clear")


###############################################################################
# Get Mass Center
# ~~~~~~~~~~~~~~~~~~~~~
# Field Calculator is used to get mass center.
xval = m3d.post.get_scalar_field_value("CM_X", None)
yval = m3d.post.get_scalar_field_value("CM_Y", None)
zval = m3d.post.get_scalar_field_value("CM_Z", None)


###############################################################################
# Create Variables
# ~~~~~~~~~~~~~~~~~~~~~
# Variables will be created with Mass Center values.
m3d[magnet.name + "x"] = str(xval * 1e3) + "mm"
m3d[magnet.name + "y"] = str(yval * 1e3) + "mm"
m3d[magnet.name + "z"] = str(zval * 1e3) + "mm"


###############################################################################
# Create Coordinate System
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Parametric Coordinate System is created

cs1 = m3d.modeler.create_coordinate_system(
    [magnet.name + "x", magnet.name + "y", magnet.name + "z"], reference_cs="Global", name=magnet.name + "CS"
)


###############################################################################
# Save and Close
# ~~~~~~~~~~~~~~~~~~~~~~~~

m3d.save_project(os.path.join(tmpfold, "magnet.aedt"))
m3d.release_desktop(close_projects=True, close_desktop=True)
