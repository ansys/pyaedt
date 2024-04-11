"""
Maxwell 2D Electrostatic analysis
---------------------------------
This example shows how you can use PyAEDT to create a Maxwell 2D electrostatic analysis.
It shows how to create the geometry, load material properties from an Excel file and
set up the mesh settings. Moreover, it focuses on post-processing operations, in particular how to
plot field line traces, relevant for an electrostatic analysis.
"""
#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import pyaedt

##########################################################
# Set AEDT version
# ~~~~~~~~~~~~~~~~
# Set AEDT version.

aedt_version = "2024.1"

#################################################################################
# Initialize Maxwell 2D
# ~~~~~~~~~~~~~~~~~~~~~
# Initialize Maxwell 2D, providing the version, path to the project, and the design
# name and type.

setup_name = 'MySetupAuto'
solver = 'Electrostatic'
design_name = 'Design1'
project_name = pyaedt.generate_unique_project_name()
non_graphical = False

#################################################################################
# Download .xlsx file
# ~~~~~~~~~~~~~~~~~~~
# Set local temporary folder to export the .xlsx file to.

file_name_xlsx = pyaedt.downloads.download_file("field_line_traces", "my_copper.xlsx")

#################################################################################
# Initialize dictionaries
# ~~~~~~~~~~~~~~~~~~~~~~~
# Initialize dictionaries that contain all the definitions for the design variables.

geom_params_circle = {
    'circle_x0': '-10mm',
    'circle_y0': '0mm',
    'circle_z0': '0mm',
    'circle_axis': 'Z',
    'circle_radius': '1mm'
}

geom_params_rectangle = {
    'r_x0': '1mm',
    'r_y0': '5mm',
    'r_z0': '0mm',
    'r_axis': 'Z',
    'r_dx': '-1mm',
    'r_dy': '-10mm'
}

##################################################################################
# Launch Maxwell 2D
# ~~~~~~~~~~~~~~~~~
# Launch Maxwell 2D and save the project.

M2D = pyaedt.Maxwell2d(projectname=project_name,
                       specified_version=aedt_version,
                       designname=design_name,
                       solution_type=solver,
                       new_desktop_session=True,
                       non_graphical=non_graphical
                       )

##################################################################################
# Create object to access 2D modeler
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the object ``mod2D`` to access the 2D modeler easily.

mod2D = M2D.modeler
mod2D.delete()
mod2D.model_units = "mm"

##################################################################################
# Define variables from dictionaries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define design variables from the created dictionaries.

for k, v in geom_params_circle.items():
    M2D[k] = v
for k, v in geom_params_rectangle.items():
    M2D[k] = v

##################################################################################
# Read materials from .xslx file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read materials from .xslx file into and set into design.

mats = M2D.materials.import_materials_from_excel(file_name_xlsx)

##################################################################################
# Create design geometries
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create rectangle and a circle and assign the material read from the .xlsx file.
# Create two new polylines and a region.

rect = mod2D.create_rectangle(position=['r_x0', 'r_y0', 'r_z0'],
                              dimension_list=['r_dx', 'r_dy', 0],
                              name='Ground', matname=mats[0])
rect.color = (0, 0, 255)  # rgb
rect.solve_inside = False

circle = mod2D.create_circle(position=['circle_x0', 'circle_y0', 'circle_z0'], radius='circle_radius',
                             num_sides='0', is_covered=True, name='Electrode', matname=mats[0])
circle.color = (0, 0, 255)  # rgb
circle.solve_inside = False

poly1_points = [[-9, 2, 0], [-4, 2, 0], [2, -2, 0],[8, 2, 0]]
poly2_points = [[-9, 0, 0], [9, 0, 0]]
poly1_id = mod2D.create_polyline(position_list=poly1_points,segment_type='Spline', name='Poly1')
poly2_id = mod2D.create_polyline(position_list=poly2_points, name='Poly2')
mod2D.split([poly1_id, poly2_id], 'YZ', sides='NegativeOnly')
mod2D.create_region([20, 100, 20, 100])

##################################################################################
# Define excitations
# ~~~~~~~~~~~~~~~~~~
# Assign voltage excitations to rectangle and circle.

M2D.assign_voltage(rect.id, amplitude=0, name='Ground')
M2D.assign_voltage(circle.id, amplitude=50e6, name='50kV')

##################################################################################
# Create initial mesh settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assign a surface mesh to the rectangle.

M2D.mesh.assign_surface_mesh_manual(assignment=['Ground'], surface_deviation=0.001)

##################################################################################
# Create, validate and analyze the setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create, update, validate and analyze the setup.

setup = M2D.create_setup(name=setup_name)
setup.props['PercentError'] = 0.5
setup.update()
M2D.validate_simple()
M2D.analyze_setup(setup_name)

##################################################################################
# Evaluate the E Field tangential component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Evaluate the E Field tangential component along the given polylines.
# Add these operations to the Named Expression list in Field Calculator.

fields = M2D.ofieldsreporter
fields.CalcStack("clear")
fields.EnterQty("E")
fields.EnterEdge("Poly1")
fields.CalcOp("Tangent")
fields.CalcOp("Dot")
fields.AddNamedExpression("e_tan_poly1", "Fields")
fields.EnterQty("E")
fields.EnterEdge("Poly2")
fields.CalcOp("Tangent")
fields.CalcOp("Dot")
fields.AddNamedExpression("e_tan_poly2", "Fields")

##################################################################################
# Create Field Line Traces Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Field Line Traces Plot specifying as seeding faces
# the ground, the electrode and the region
# and as ``In surface objects`` only the region.

plot = M2D.post.create_fieldplot_line_traces(seeding_faces=["Ground", "Electrode", "Region"],
                                             in_volume_tracing_objs="Region", plot_name="LineTracesTest")

###################################################################################
# Update Field Line Traces Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Update field line traces plot.
# Update seeding points number, line style and line width.

plot.SeedingPointsNumber = 20
plot.LineStyle = "Cylinder"
plot.LineWidth = 3
plot.update()

###################################################################################
# Export field line traces plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export field line traces plot.
# For field lint traces plot, the export file format is ``.fldplt``.

M2D.post.export_field_plot(plot_name="LineTracesTest", output_dir=M2D.toolkit_directory, file_format="fldplt")

##########################################################
# Export a field plot to an image file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export the flux lines plot to an image file using PyVista Python package.

M2D.post.plot_field_from_fieldplot(plot.name, show=False)

##########################################################
# Export the mesh field plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Export the mesh in ``aedtplt`` format.

M2D.post.export_mesh_obj(setup=M2D.nominal_adaptive)

###################################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and close AEDT.

M2D.save_project()
M2D.release_desktop()
