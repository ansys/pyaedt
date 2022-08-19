"""
HFSS: spiral inductor
---------------------
This example shows how you can use PyAEDT to create a spiral inductor, solve it, and plot results.
"""

#############################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
from pyaedt import Hfss, constants
from pyaedt import generate_unique_project_name


project_name = generate_unique_project_name(project_name="spiral")

#############################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical model. ``"PYAEDT_NON_GRAPHICAL"``` is needed to
# generate documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

#############################################################
# Launch HFSS
# ~~~~~~~~~~~
# Launch HFSS 2022 R2 in non-graphical mode and change the
# units to microns.

hfss = Hfss(specified_version="2022.2", non_graphical=non_graphical, designname="A1")
hfss.modeler.model_units = "um"
p = hfss.modeler

#############################################################
# Define variables
# ~~~~~~~~~~~~~~~~
# Define input variables. You can use the values that follow or edit
# them.

rin = 10
width = 2
spacing = 1
thickness = 1
Np = 8
Nr = 10
gap = 3
Tsub = 6


#############################################################
# Standardize polyline
# ~~~~~~~~~~~~~~~~~~~~
# Standardize the polyline using the ``create_line`` method to fix
# the width, thickness, and material.

def create_line(pts):
    p.create_polyline(pts, xsection_type="Rectangle", xsection_width=width, xsection_height=thickness, matname="copper")


################################################################
# Create spiral inductor
# ~~~~~~~~~~~~~~~~~~~~~~
# Create the spiral inductor. This spiral inductor is not
# parametric, but you could parametrize it later.

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
# Center return path
# ~~~~~~~~~~~~~~~~~~
# Center the return path.

x0, y0, z0 = ind.points[0]
x1, y1, z1 = ind.points[-1]
create_line([(x0 - width / 2, y0, -gap), (abs(x1) + 5, y0, -gap)])
p.create_box((x0 - width / 2, y0 - width / 2, -gap - thickness / 2), (width, width, gap + thickness), matname="copper")

################################################################
# Create port 1
# ~~~~~~~~~~~~~
# Create port 1.

p.create_rectangle(
    constants.PLANE.YZ, (abs(x1) + 5, y0 - width / 2, -gap - thickness / 2), (width, -Tsub + gap), name="port1"
)
hfss.create_lumped_port_to_sheet(sheet_name="port1", axisdir=constants.AXIS.Z)


################################################################
# Create port 2
# ~~~~~~~~~~~~~
# Create port 2.

create_line([(x1 + width / 2, y1, 0), (x1 - 5, y1, 0)])
p.create_rectangle(constants.PLANE.YZ, (x1 - 5, y1 - width / 2, -thickness / 2), (width, -Tsub), name="port2")
hfss.create_lumped_port_to_sheet(sheet_name="port2", axisdir=constants.AXIS.Z)


################################################################
# Create silicon substrate and ground plane
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the silicon substrate and the ground plane.

p.create_box([x1 - 20, x1 - 20, -Tsub - thickness / 2], [-2 * x1 + 40, -2 * x1 + 40, Tsub], matname="silicon")

p.create_box([x1 - 20, x1 - 20, -Tsub - thickness / 2], [-2 * x1 + 40, -2 * x1 + 40, -0.1], matname="PEC")

################################################################
# Assign airbox and radiation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assign the airbox and the radiation.

box = p.create_box(
    [x1 - 20, x1 - 20, -Tsub - thickness / 2 - 0.1], [-2 * x1 + 40, -2 * x1 + 40, 100], name="airbox", matname="air"
)

hfss.assign_radiation_boundary_to_objects("airbox")

################################################################
# Assign material override
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Assign a material override so that the validation check does
# not fail.

hfss.change_material_override()


###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

hfss.plot(show=False, export_path=os.path.join(hfss.working_directory, "Image.jpg"), plot_air_objects=False)


################################################################
# Create setup
# ~~~~~~~~~~~~
# Create the setup and define a frequency sweep to solve the project.

setup1 = hfss.create_setup(setupname="setup1")
setup1.props["Frequency"] = "10GHz"
hfss.create_linear_count_sweep("setup1", "GHz", 1e-3, 50, 451, sweep_type="Interpolating")
hfss.save_project()
hfss.analyze_all()

################################################################
# Get report data
# ~~~~~~~~~~~~~~~
# Get report data and use the following formulas to calculate
# the inductance and quality factor.

L_formula = "1e9*im(1/Y(1,1))/(2*pi*freq)"
Q_formula = "im(Y(1,1))/re(Y(1,1))"

################################################################
# Plot calculated values in Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot the calculated values in Matplotlib.

x = hfss.post.get_solution_data([L_formula, Q_formula])
x.plot([L_formula, Q_formula], math_formula="re", xlabel="Freq", ylabel="L and Q")


################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

hfss.save_project(project_name)
if os.name != "posix":
    hfss.release_desktop()
