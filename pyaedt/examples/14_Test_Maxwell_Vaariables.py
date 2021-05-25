# ------------------------------------------------------------------------------
#
# This Example shows how to create and manage variables
# NOTE This example produces and error at the moment
#
# -------------------------------------------------------------------------------
from pyaedt import Desktop
from pyaedt import Maxwell2d, Maxwell3d
from pyaedt.application.Variables import Variable, VariableManager

with Desktop(specified_version="2021.1"):
    M2D = Maxwell2d()
    udp = M2D.Position(0, 0, 0)
    obj_id = M2D.modeler.primitives.create_rectangle(M2D.CoordinateSystemPlane.XYPlane,udp,[10, 20], name="My_Box")  # All positions in model units
    M2D.modeler.primitives.get_obj_name(obj_id)
    M2D.modeler.primitives.get_object_faces(obj_id)
    M3D = Maxwell3d()

    my_var = Variable('23mV')
    b = my_var.value
    c = my_var.numeric_value
    d = my_var.format('.4e')
    e = my_var.string_value
    my_var.rescale_to('dBV')
    f = my_var.string_value
    my_var_temp = Variable('373kel')
    my_var_temp.rescale_to('fah')

    M2D["$Test_Prj_1"] = my_var
    g = M2D["$Test_Prj_1"]

    M2D["$Test_Prj_2"] = my_var_temp
    k = M2D["$Test_Prj_2"]
    M2D["Massimo"]="1W"

    var_mgr = VariableManager(M2D)

    g = var_mgr["$Test_Prj_1"]
    h = var_mgr["$Test_Prj_2"]
    var_mgr["Var_1"] = "50mm"

    pass

