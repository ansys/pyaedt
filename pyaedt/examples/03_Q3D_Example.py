# ------------------------------------------------------------------------------
#
# This Example shows how to create a full project from scratch in Q3D. the project creates
# a setup, solves it
#
# -------------------------------------------------------------------------------
import os

from pyaedt import Q3d
from pyaedt import Desktop
from pyaedt.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise03"
project_file = os.path.join(project_dir, project_name + ".aedt")

desktopVersion = "2021.1"
NonGraphical = False
NewThread = False
with Desktop(desktopVersion, NonGraphical, NewThread):
    q3d = Q3d()
    udp = q3d.modeler.Position(0, 0, 0)
    coax_dimension = 30
    id1 = q3d.modeler.primitives.create_cylinder(q3d.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension, 0,
                                                 matname="brass", name="MyCylinder")
    mysetup = q3d.create_setup()
    mysetup.props["SaveFields"] = True
    mysetup.update()
    source = q3d.assign_source_to_objectface("MyCylinder", axisdir=0)
    sink = q3d.assign_sink_to_objectface("MyCylinder", axisdir=3)
    q3d.auto_identify_nets()
    q3d.save_project(project_file)
    q3d.analyse_nominal()
    surflist = q3d.modeler.primitives.get_object_faces("MyCylinder")

pass
