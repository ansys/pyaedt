"""

Q3D Bus Bar Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a BusBar Project in
in Q3D and run a simulation
"""
# sphinx_gallery_thumbnail_path = 'Resources/busbar.png'

import os

from pyaedt.desktop import Desktop
from pyaedt import Q3d

###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode

NonGraphical = True

###############################################################################
# Launch Desktop and Q3D
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples will use AEDT 2021.1 in Graphical mode

# This examples will use SI units.

d = Desktop("2021.1", NonGraphical, False)

q=Q3d()

###############################################################################
# Primitives Creation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here pyaedt will create polylines for the three busbar and box for the substrate


q.modeler.primitives.create_polyline([[0, 0, 0], [-100, 0, 0]], name="Bar1", matname="copper", xsection_type="Rectangle",
                                     xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_polyline([[0, -15, 0], [-150, -15, 0]], name="Bar2", matname="aluminum",
                                     xsection_type="Rectangle", xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_polyline([[0, -30, 0], [-175, -30, 0], [-175, -10, 0]], name="Bar3", matname="copper",
                                     xsection_type="Rectangle", xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_box([50,30,-0.5], [-250,-100,-3], name="substrate", matname="FR4_epoxy")

###############################################################################
# Boundary Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here pyaedt will identify nets and assign source and sink to all nets
# There will be a source and sink for each bus bar

q.auto_identify_nets()

q.assign_source_to_objectface("Bar1",axisdir=q.AxisDir.XPos, source_name="Source1")

q.assign_sink_to_objectface("Bar1",axisdir=q.AxisDir.XNeg, sink_name="Sink1")

q.assign_source_to_objectface("Bar2",axisdir=q.AxisDir.XPos, source_name="Source2")
q.assign_sink_to_objectface("Bar2",axisdir=q.AxisDir.XNeg, sink_name="Sink2")
q.assign_source_to_objectface("Bar3",axisdir=q.AxisDir.XPos, source_name="Source3")
q.assign_sink_to_objectface("Bar3",axisdir=q.AxisDir.YPos, sink_name="Sink3")


###############################################################################
# Add a Q3D Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a setup to the project and define Adaptive Frequency value

q.create_setup(props={"AdaptiveFreq":"100MHz"})

###############################################################################
# Create AEDT Rectangular Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a rectangular plot to Aedt
q.post.create_rectangular_plot("C(Bar1,Bar1)",context="Original")

###############################################################################
# Solve Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method solve setup
q.analyse_nominal()

###############################################################################
# Close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton is completed user can close the desktop or release it (using release_desktop method).
# All methods give possibility to save projects before exit
if os.name != "posix":
    d.force_close_desktop()


