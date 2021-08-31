"""
Q3D Busbar Analysis
-------------------
This example shows how you can use PyAEDT to create a busbar design in
in Q3D and run a simulation.
"""
# sphinx_gallery_thumbnail_path = 'Resources/busbar.png'

import os

from pyaedt.desktop import Desktop
from pyaedt import Q3d

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch
# AEDT in graphical mode.

NonGraphical = True

###############################################################################
# Launch AEDT and Q3D
# ~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2021.1 in graphical mode.

# This example use SI units.

d = Desktop("2021.1", NonGraphical, False)

q=Q3d()

###############################################################################
# Create Primitives
# ~~~~~~~~~~~~~~~~~
# Create polylines for three busbars and a box for the substrate.

q.modeler.primitives.create_polyline([[0, 0, 0], [-100, 0, 0]], name="Bar1", matname="copper", xsection_type="Rectangle",
                                     xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_polyline([[0, -15, 0], [-150, -15, 0]], name="Bar2", matname="aluminum",
                                     xsection_type="Rectangle", xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_polyline([[0, -30, 0], [-175, -30, 0], [-175, -10, 0]], name="Bar3", matname="copper",
                                     xsection_type="Rectangle", xsection_width="5mm", xsection_height="1mm")

q.modeler.primitives.create_box([50,30,-0.5], [-250,-100,-3], name="substrate", matname="FR4_epoxy")

###############################################################################
# Set Up Boundaries
# ~~~~~~~~~~~~~~~~~
# Identify nets and assign sources and sinks to all nets.
# There is a source and sink for each busbar.

q.auto_identify_nets()

q.assign_source_to_objectface("Bar1",axisdir=q.AxisDir.XPos, source_name="Source1")

q.assign_sink_to_objectface("Bar1",axisdir=q.AxisDir.XNeg, sink_name="Sink1")

q.assign_source_to_objectface("Bar2",axisdir=q.AxisDir.XPos, source_name="Source2")
q.assign_sink_to_objectface("Bar2",axisdir=q.AxisDir.XNeg, sink_name="Sink2")
q.assign_source_to_objectface("Bar3",axisdir=q.AxisDir.XPos, source_name="Source3")
q.assign_sink_to_objectface("Bar3",axisdir=q.AxisDir.YPos, sink_name="Sink3")


###############################################################################
# Add a Q3D Setup
# ~~~~~~~~~~~~~~~
# This command adds a setup to the project and defines the adaptive frequency
# value.

q.create_setup(props={"AdaptiveFreq":"100MHz"})

###############################################################################
# Create a Rectangular Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This command creates a rectangular plot.

q.post.create_rectangular_plot("C(Bar1,Bar1)",context="Original")

###############################################################################
# Solve the Setup
# ~~~~~~~~~~~~~~~
# This command solves the setup.

q.analyze_nominal()

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# `release_desktop` method.
# All methods provide for saving projects before exiting.
if os.name != "posix":
    d.force_close_desktop()
