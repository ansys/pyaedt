"""
Spiral Inductor Example
-----------------------
This example shows how you can use PyAEDT to create a spiral inductor, solve it and plot results.
"""
# sphinx_gallery_thumbnail_path = 'Resources/spiral.png'

#############################################################
# Import packages
#

import os
import matplotlib.pyplot as plt
from pyaedt import Hfss, constants


#############################################################
# Launch Hfss 2021.2 in non graphical mode.
# Change units to micron
hfss = Hfss(specified_version="2021.2", non_graphical=False, designname="A1")
hfss.modeler.model_units = "um"
p = hfss.modeler.primitives

#############################################################
# Input Variables. Edit it to change your inductor.
#
rin = 10
width = 2
spacing = 1
thickness = 1
Np = 8
Nr = 10
gap = 3
Tsub = 6


#############################################################
# This method standardizes the usage of polyline in this
# example by fixing the width, thickness and material.
#
def create_line(pts):
    p.create_polyline(pts, xsection_type="Rectangle", xsection_width=width, xsection_height=thickness, matname="copper")


################################################################
# Here a spiral inductor is created.
# Spiral is not parameteric but could be parametrized later on.
#

ind = hfss.modeler.create_spiral(
    internal_radius=rin,
    width=width,
    spacing=spacing,
    turns=Nr,
    faces=Np,
    thickness=thickness,
    material="copper",
    name="Inductor1",
)


################################################################
# Center Return Path.
#

x0, y0, z0 = ind.points[0]
x1, y1, z1 = ind.points[-1]
create_line([(x0 - width / 2, y0, -gap), (abs(x1) + 5, y0, -gap)])
p.create_box((x0 - width / 2, y0 - width / 2, -gap - thickness / 2), (width, width, gap + thickness), matname="copper")

################################################################
# Port 1 creation.
#
p.create_rectangle(
    constants.PLANE.YZ, (abs(x1) + 5, y0 - width / 2, -gap - thickness / 2), (width, -Tsub + gap), name="port1"
)
hfss.create_lumped_port_to_sheet(sheet_name="port1", axisdir=constants.AXIS.Z)


################################################################
# Port 2 creation.
#
create_line([(x1 + width / 2, y1, 0), (x1 - 5, y1, 0)])
p.create_rectangle(constants.PLANE.YZ, (x1 - 5, y1 - width / 2, -thickness / 2), (width, -Tsub), name="port2")
hfss.create_lumped_port_to_sheet(sheet_name="port2", axisdir=constants.AXIS.Z)


################################################################
# Silicon Substrate and Ground plane.
#
p.create_box([x1 - 20, x1 - 20, -Tsub - thickness / 2], [-2 * x1 + 40, -2 * x1 + 40, Tsub], matname="silicon")

p.create_box([x1 - 20, x1 - 20, -Tsub - thickness / 2], [-2 * x1 + 40, -2 * x1 + 40, -0.1], matname="PEC")

################################################################
# Airbox and radiation assignment.
#
box = p.create_box(
    [x1 - 20, x1 - 20, -Tsub - thickness / 2 - 0.1], [-2 * x1 + 40, -2 * x1 + 40, 100], name="airbox", matname="air"
)

hfss.assign_radiation_boundary_to_objects("airbox")

################################################################
# Material override is needed to avoid validation check to fail.
#
hfss.change_material_override()

################################################################
# Create a setup and define a frequency sweep.
# Project will be solved after that.

setup1 = hfss.create_setup(setupname="setup1")
setup1.props["Frequency"] = "10GHz"
hfss.create_linear_count_sweep("setup1", "GHz", 1e-3, 50, 451, sweep_type="Interpolating")
setup1.update()
hfss.save_project()
hfss.analyze_all()

################################################################
# Get Report Data and plot it on matplotlib.
# Inductance.
L_formula = "1e9*im(1/Y(1,1))/(2*pi*freq)"
x = hfss.post.get_report_data(L_formula)

plt.plot(x.sweeps["Freq"], x.data_real(L_formula))

plt.grid()
plt.xlabel("Freq")
plt.ylabel("L(nH)")
plt.show()

plt.clf()


################################################################
# Get Report Data and plot it on matplotlib.
# Quality Factor.

Q_formula = "im(Y(1,1))/re(Y(1,1))"
x = hfss.post.get_report_data(Q_formula)
hfss.save_project()

plt.plot(x.sweeps["Freq"], x.data_real(Q_formula))
plt.grid()
plt.xlabel("Freq")
plt.ylabel("Q")
plt.show()

################################################################
# Get Report Data and plot it on matplotlib.
# Save and close the project.

hfss.save_project()
if os.name != "posix":
    hfss.release_desktop()
