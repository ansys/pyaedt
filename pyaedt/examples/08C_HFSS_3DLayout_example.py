# ------------------------------------------------------------------------------
#
# This Example shows how to create a geometry and stackup in HFSS3DLayout
#
# -------------------------------------------------------------------------------
try:
    from pyaedt import Hfss3dLayout
    from pyaedt import Desktop
except:
    from pyaedt import Hfss3dLayout
    from pyaedt import Desktop

desktopVersion = "2021.1"
oDesktop = None
NonGraphical = False
NewThread = False
with Desktop(desktopVersion, NonGraphical, NewThread):
    hfss3dlayout = Hfss3dLayout()
    mymat = hfss3dlayout.materials.creatematerial("myMaterial")
    mymat.set_property_value(mymat.PropName.Permittivity, 4.1)
    mymat.set_property_value("Conductivity", 100)
    mymat.set_property_value("Young's Modulus", 1e10)
    mymat.update()
    s1 = hfss3dlayout.modeler.layers.add_layer("Signal1", "signal", 0.035, 0)
    d2 = hfss3dlayout.modeler.layers.add_layer("Diel1", "dielectric", 1, 0,"myMaterial")
    s3 = hfss3dlayout.modeler.layers.add_layer("Signal3", "signal", 0.035, 1)
    n3 = hfss3dlayout.modeler.primitives.create_rectangle(s3.name, 0, 0, 20, 5, 0, 0, "myrectangle")
    a = hfss3dlayout.modeler.primitives.geometries
    print(len(a))
    p1 = hfss3dlayout.create_edge_port("myrectangle", 1)
    p2 = hfss3dlayout.create_pin_port("P2", 19, 2.5, 0)
    via = hfss3dlayout.modeler.primitives.create_via(x=10, y=2, name="MyVia")
    p3 = hfss3dlayout.create_coax_port("MyVia", "Signal3", 10, 10.5, 2.5, 3)
    s3.thickness = 1
    s3.toprounghenss = 3
    s3.HRatio = 3.5
    s3.update_stackup_layer()

    pad1 = hfss3dlayout.modeler.primitives.new_padstack("My_padstack2")
    hole1 = pad1.add_hole()
    pad1.add_layer("Start", pad_hole=hole1, thermal_hole=hole1)
    hole2 = pad1.add_hole(holetype="Rct", sizes=[0.5, 0.8])
    pad1.add_layer("Default", pad_hole=hole2, thermal_hole=hole2)
    pad1.add_layer("Stop", pad_hole=hole1, thermal_hole=hole1)
    pad1.hole.sizes = ['0.8mm']
    pad1.plating = 70
    pad1.create()
    
print("done")

