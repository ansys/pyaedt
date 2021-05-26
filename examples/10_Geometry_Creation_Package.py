# ------------------------------------------------------------------------------
#
# This Example shows how to create a geometry in HFSS using pyaedt. The specific example creates a multilayer structure (package)
#
# -------------------------------------------------------------------------------
import os
from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise10"

with Desktop("2021.1"):
    hfss = Hfss()
    hfss.modeler.model_units = "mm"
    hfss["board_x"] = "10mm"
    hfss["board_w"] = "20mm"
    hfss["board_thickness"] = "2.5mm"
    center = hfss.modeler.Position("-board_x/2", "-board_w/2", 0)
    brd = hfss.modeler.primitives.create_box(center, ["board_x", "board_w", "board_thickness"], "Board", "Fr4_epoxy")
    hfss.modeler.oeditor.CloseAllWindows()
    die_met=1
    die_diel = 10
    hfss["die_met_thickness"] = str(die_met)+"um"
    hfss["die_diel_thickness"] = str(die_diel)+"um"
    initial_el = "board_thickness"
    hfss["die_dimx"] = "1mm"
    hfss["die_dimy"] = "2mm"

    k = 0
    el = initial_el
    listtop = {}
    face_centroids = {}
    while k < 11:
        center = hfss.modeler.Position(0, 0, el)
        if divmod(k, 2)[1] == 0:
            pkg = hfss.modeler.primitives.create_box(center, ["die_dimx", "die_dimy", "die_met_thickness"], "die" + str(k),"copper")
        else:
            pkg = hfss.modeler.primitives.create_box(center, ["die_dimx", "die_dimy", "die_diel_thickness"], "die" + str(k),"gallium_arsenide")

        # hfss.materials.assignmaterial(hfss.modeler.primitives.get_obj_name(pkg), "copper", False, False)
        cs = hfss.modeler.coordinate_system
        cs.create(["die_dimx/2", "die_dimy/2", 0], "XY")
        hfss.modeler.split(hfss.modeler.primitives.get_obj_name(pkg), hfss.CoordinateSystemPlane.ZXPlane)
        hfss.modeler.split(hfss.modeler.primitives.get_obj_name(pkg), hfss.CoordinateSystemPlane.YZPlane)
        hfss.modeler.primitives.refresh()
        names = hfss.modeler.primitives.get_all_objects_names()
        split = []
        for nm in names:
            if hfss.modeler.primitives.get_obj_name(pkg) in nm:
                split.append(nm)
                faces = hfss.modeler.primitives.get_object_faces(hfss.modeler.primitives.get_obj_id(nm))
                minf = 1e9
                maxf = -1e9
                for face in faces:
                    pos = hfss.modeler.oeditor.GetFaceCenter(int(face))
                    if float(pos[2]) > maxf:
                        topf = pos
                        maxf = float(pos[2])
                    if float(pos[2]) < minf:
                        botf = pos
                        minf = float(pos[2])
                face_centroids[nm] = [topf, botf]

        cs.setWorkingCoordinateSystem("Global")

        if divmod(k,2)[1]==0:
            el += "+" + str(die_met) + "um"
        else:
            el += "+" + str(die_diel) + "um"
        k += 1

    with open(os.path.join(project_dir, project_name + "_faces.txt"), "w") as f:
        for name in face_centroids:
            line = name + ";" + str(face_centroids[name][0]) + ";" + str(face_centroids[name][1]) + "\n"
            f.write(line)
    hfss.oproject.SetActiveDesign(hfss.design_name)
    hfss.modeler.fit_all()



