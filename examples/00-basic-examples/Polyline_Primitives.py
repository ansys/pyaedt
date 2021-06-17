"""
Polyline Example Analysis
--------------------------------------------
This tutorial shows how you can create and manipulate polylines using pyaedt
"""

#########################################################################
# #### Perform required imports from AEDTLib and connect to the Desktop

import os
from IPython.display import Image, display
from pyaedt.maxwell import Maxwell3d
from pyaedt.modeler.Primitives import Polyline, PolylineSegment

#########################################################################
# ### Create a Maxwell3D object  and set the unit type to mm

M3D = Maxwell3d(solution_type="Transient", designname="test_polyline_3D", specified_version="2021.1")
M3D.modeler.model_units = "mm"
prim3D = M3D.modeler.primitives

#########################################################################
# ### Clear any existing objects

prim3D.delete(prim3D.get_all_objects_names())

#########################################################################
# ### Define some design Variables as parameters for the polyline objects

M3D["p1"] = "100mm"
M3D["p2"] = "71mm"

#########################################################################
# #### Input Data
# All data for the polyline functions can be entered either as floating-point numbers or string expressions. Floating-point values are assumed to be in model-units (M3D.modeler.model_units)

test_points = [ ["0mm",       "p1",    "0mm"],
                ["-p1",       "0mm",   "0mm"],
                ["-p1/2",     "-p1/2",   "0mm"],
                ["0mm",         "0mm", "0mm"]]

#########################################################################
# #### Polyline primitives
# ##### Line Primitive
# 
# The basic polyline command takes a list of positions (list of [X, Y, Z] coordinates) and creates a polyline object with one or more segments. The supported segment types are: 
# 
# <ul>
# <li>Line </li>
# <li>Arc (3-points)</li>
# <li>AngularArc (center-point + angle)</li>
# <li>Spline</li>    
# </ul>

P = prim3D.create_polyline(position_list=test_points[0:2], name="PL01_line")

print("Created Polyline with name: {}".format(prim3D.objects[P.id].name))
print("Segment types : {}".format(P._segment_types))
print("primitive id = {}".format(P.id))

#########################################################################
# #### Arc (3-point) primitive
# position_list must contain at least 3 positions. The first 3 are taken

P = prim3D.create_polyline(position_list=test_points[0:3], segment_type="Arc", name="PL02_arc")

print("Created new object with id {} and name {}".format(P.id, prim3D.objects[P.id].name))

#########################################################################
# #### Spline primitive 
# Here we define the segment using a PolylineSegment object. This gives us additional input parameters such as the number of points to define the spline (in this case 4). The input position_list must contain at least 4 position values

P = prim3D.create_polyline(position_list=test_points, segment_type=PolylineSegment("Spline", num_points=4),
                           name="PL03_spline_4pt")

#########################################################################
# #### center-point arc primitive
# A center-point arc segment is defined by a starting point, a center point and an angle of rotation around the center point. The rotation occurs in a plane parallel to the XY, YZ or ZX plane of the active coordinate system. The starting-point and the center point must therefore have one coordinate value (X, Y, or Z) which has the same value.

# Here the start-point and the center-point have a common z-coordinate "0mm". The curve will therefore be rotated in the XY plane with Z = "0mm"

start_point = [100, 100, 0]
center_point = [0, 0, 0]
P = prim3D.create_polyline(position_list=[start_point],
                           segment_type=PolylineSegment("AngularArc", arc_center=center_point, arc_angle="30deg"),
                           name="PL04_center_point_arc")

#########################################################################
# Here the start point and center point have the same values in y and z, so the plane or rotation could be either XY or ZX. For these special cases when the rotation plane is ambiguous, the plane can be specified explicitly. 

start_point = [100, 0, 0]
center_point = [0, 0, 0]
P = prim3D.create_polyline(position_list=[start_point],
                           segment_type=PolylineSegment("AngularArc", arc_center=center_point, arc_angle="30deg", arc_plane="XY"),
                           name="PL04_center_point_arc_rot_XY")
P = prim3D.create_polyline(position_list=[start_point],
                           segment_type=PolylineSegment("AngularArc", arc_center=center_point, arc_angle="30deg", arc_plane="ZX"),
                           name="PL04_center_point_arc_rot_ZX")


#########################################################################
# ### Compound polyline examples
# A list of points can be use to create a multi-segment polyline in one single command.
# 
# By default, if no specification of the type of segments is given, then all the points will be connected by line segments. 

P = prim3D.create_polyline(position_list=test_points, name="PL06_segmented_compound_line")

#########################################################################
# We can specify the segment types with the input variable segment_type. In this case we specify that the four input points in position_list are to be connected as a "Line" segment followed ba a 3-point "Arc segment

P = prim3D.create_polyline(position_list=test_points, segment_type=["Line", "Arc"], name="PL05_compound_line_arc")

#########################################################################
# The input argument close_surface ensures that the polyline start-point and end-point are the same. If necessary an additional line-segment is added to achieve this.

P = prim3D.create_polyline(position_list=test_points,
                           close_surface=True,
                           name="PL07_segmented_compound_line_closed")

#########################################################################
# The input argument cover_surface=True performs the modeler command cover_surface additionally. Note that specifying cover_surface=True autmatically results in the polyline being closed. 

P = prim3D.create_polyline(position_list=test_points,
                           cover_surface=True,
                           name="SPL01_segmented_compound_line")

#########################################################################
# #### Compound line - insert a line segment
# Here we define a line segment starting at vertex 1 ["100mm", "0mm", "0mm"] of an existing polyline, and ending at some new point ["90mm", "20mm", "0mm"]. By numerical comparison of the start point with the existing vertices of the original polyline object it is determined automatically that the segment is inserted after the first segment of the original polyline.

P = prim3D.create_polyline(position_list=test_points,
                           close_surface=True,
                           name="PL08_segmented_compound_insert_segment")

start_point = P.start_point
insert_point = ["90mm", "20mm", "0mm"]


P.insert_segment(position_list=[start_point, insert_point])

#########################################################################
# #### Compound line with insert curve
# Here we define a line segment starting at vertex 1 ["100mm", "0mm", "0mm"] of an existing polyline, and ending at some new point ["90mm", "20mm", "0mm"]. By numerical comparison of the start oint it is determined automatically that the segment is inserted after the first segment of the original polyline.
# 

P = prim3D.create_polyline(position_list=test_points,
                           close_surface=False,
                           name="PL08_segmented_compound_insert_arc")


start_point = P.vertex_positions[1]
insert_point1 = ["90mm", "20mm", "0mm"]
insert_point2 = [40, 40, 0]

P.insert_segment(position_list=[start_point, insert_point1, insert_point2], segment="Arc")

#########################################################################
# ##### Special case: inserting at the end of a center-point arc (type="AngularArc")
# Step 1: Draw a center-point arc

start_point = [2200.0,0.0,1200.0]
arc_center_1 = [1400 ,0 ,800]
arc_angle_1 = "43.47deg"

P = prim3D.create_polyline(name="First_Arc",
                           position_list=[start_point],
                           segment_type=PolylineSegment(type='AngularArc',
                                                      arc_angle=arc_angle_1, 
                                                      arc_center=arc_center_1))

#########################################################################
# Step 2: Now insert a line segment at the end of the arc with a specified end point. 

start_of_line_segment = P.end_point
end_of_line_segment = [3600, 200, 30]

P.insert_segment(position_list=[start_of_line_segment, end_of_line_segment])

#########################################################################
# Step 3: Now append a center-point arc segment to the line object

arc_angle_2 = "39.716deg"
arc_center_2 = [3400 ,200 ,3800]

P.insert_segment(position_list=[end_of_line_segment],
                 segment=PolylineSegment(type="AngularArc", 
                                         arc_center=arc_center_2, 
                                         arc_angle=arc_angle_2))

#########################################################################
# Here we show how to complete all three steps in one using a compound polyline definition

prim3D.create_polyline(position_list=[start_point, end_of_line_segment],
                       segment_type=[PolylineSegment(type='AngularArc', arc_angle="43.47deg", arc_center=arc_center_1),
                                        PolylineSegment(type="Line"),
                                        PolylineSegment(type='AngularArc', arc_angle=arc_angle_2, arc_center=arc_center_2)],
                       name="Compound_Polyline_One_Command")

#########################################################################
# Two 3-point arcs forming a circle and covered. Note that the last point of the second Arc segment is not defined in the position list

P = prim3D.create_polyline(position_list=[[34.1004, 14.1248, 0],
                                          [27.646, 16.7984, 0],
                                          [24.9725, 10.3439, 0],
                                          [31.4269, 7.6704, 0]],
                           segment_type=["Arc", "Arc"],
                           cover_surface=True, close_surface=True,
                           name="Rotor_Subtract_25_0", matname="vacuum")

#########################################################################
# Another example of a complex polyline where the number of points is insufficient to populate the requested segments. This results in an IndexError which is caught silently within AEDTLib. The return value of the command is False, which can be caught at the application level. Maybe not so useful ina jupyter notebook but important for the unit tests

MDL_points = [["67.1332mm", "2.9901mm", "0mm"],
              ["65.9357mm", "2.9116mm", "0mm"],
              ["65.9839mm", "1.4562mm", "0mm"],
              ["66mm", "0mm", "0mm"],
              ["99mm", "0mm", "0mm"],
              ["98.788mm", "6.4749mm", "0mm"],
              ["98.153mm", "12.9221mm", "0mm"],
              ["97.0977mm", "19.3139mm", "0mm"]]


MDL_segments = [
    "Line", "Arc", "Line", "Arc", "Line"
]
return_value = prim3D.create_polyline(MDL_points, segment_type=MDL_segments, name="MDL_Polyline")
assert return_value   # triggers an error at the application error

#########################################################################
# And here we provide more points than the segment list requires - this is a valis usage and the remaining points are ignored

MDL_segments = ["Line", "Arc", "Line", "Arc"]

P = prim3D.create_polyline(MDL_points, segment_type=MDL_segments, name="MDL_Polyline")

#########################################################################
# #### Save the project file

project_dir=r'C:\temp'
project_name='Polylines'
project_file = os.path.join(project_dir, project_name + '.aedt')

M3D.save_project(project_file)

M3D.close_desktop()



