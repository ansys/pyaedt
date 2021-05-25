# ------------------------------------------------------------------------------
#
# This Example shows how to create a custom Arc Polyline in 3D Model Editor
#
# -------------------------------------------------------------------------------

from pyaedt import Desktop
from pyaedt import Maxwell3d

with Desktop(specified_version="2021.1"):
    M3D = Maxwell3d(solution_type="EddyCurrent")
    M3D.modeler.model_units = "mm"
    GEO = M3D.modeler
    CS = M3D.modeler.coordinate_system

    PosXYZ = M3D.modeler.Position
    point_list = []

    point_list.append(PosXYZ(1400.0, 0.0, 800.0))
    point_list.append(PosXYZ(2200.0, 0.0, 1200.0))
    point_list.append(PosXYZ(1183.069542, 0.0, 1667.721831))
    point_list.append(PosXYZ(2183.069542, 100.0, 3667.721831))
    point_list.append(PosXYZ(3400, 200, 3800))
    point_list.append(PosXYZ(3600, 200, 3000))
    MyWP = 'ZX'
    MyCW = 'cw'
    MyPolName = "cArc"

    arc = M3D.modeler.primitives.create_3pointArc(point_list, MyWP, MyCW, coversurface=False, name=MyPolName)
    M3D.modeler.primitives.insert_polyline_segment(point_list[2:], segment_type='Line', at_start=False, name=MyPolName, index=0, numpoints=2)
    M3D.modeler.primitives.insert_polyline_segment(point_list[3:], segment_type='AngularArc', at_start=False, name=MyPolName, index=1, numpoints=3)
    M3D.modeler.primitives.create_polyline_with_crosssection(MyPolName)
    M3D.modeler.fit_all()

pass
