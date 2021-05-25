# ------------------------------------------------------------------------------
# Standard Python Module Imports
import os

from pyaedt import Desktop
from pyaedt import Maxwell3d
from pyaedt import Icepak
from pyaedt.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise02"
project_file = os.path.join(project_dir, project_name + ".aedt")

with Desktop(specified_version="2021.1"):
    M3D = Maxwell3d(solution_type="EddyCurrent")
    M3D.modeler.model_units = "mm"
    GEO = M3D.modeler
    CS = M3D.modeler.coordinate_system
    plate_pos = M3D.modeler.Position(0, 0, 0)
    hole_pos = M3D.modeler.Position(18, 18, 0)
    # Create plate with hole
    plate = GEO.primitives.create_box(plate_pos, [294, 294, 19], name="Plate")  # All positions in model units
    hole = GEO.primitives.create_box(hole_pos, [108, 108, 19], name="Hole")  # All positions in model units
    GEO.subtract([plate], [hole])
    M3D.assignmaterial(plate, "aluminum")
    M3D.solve_inside("Plate")
    p_plate = M3D.post.volumetric_loss("Plate")

    # Create coil
    center_hole = M3D.modeler.Position(119, 25, 49)
    center_coil = M3D.modeler.Position(94, 0, 49)
    coil_hole = GEO.primitives.create_box(center_hole, [150, 150, 100], name="Coil_Hole")  # All positions in model units
    coil = GEO.primitives.create_box(center_coil, [200, 200, 100], name="Coil")  # All positions in model units
    GEO.subtract([coil], [coil_hole])
    M3D.assignmaterial(coil, "copper")
    M3D.solve_inside("Coil")
    p_coil = M3D.post.volumetric_loss("Coil")

    # Create relative coordinate system
    CS.create([200, 100, 0], view="XY", name="Coil_CS")

    # Create coil terminal
    GEO.section(["Coil"], M3D.CoordinateSystemPlane.ZXPlane)
    GEO.separate_bodies(["Coil_Section1"])
    GEO.primitives.delete("Coil_Section1_Separate1")

    M3D.assign_current(["Coil_Section1"], amplitude=2472)

    # draw region
    M3D.modeler.create_air_region(*[300] * 6)

    # set eddy effects
    adaptive_frequency = "200Hz"
    M3D.eddy_effects_on(['Plate'])
    Setup = M3D.create_setup()
    Setup.props["MaximumPasses"] = 12
    Setup.props["MinimumPasses"] = 2
    Setup.props["MinimumConvergedPasses"] = 1
    Setup.props["PercentRefinement"] = 30
    Setup.props["Frequency"] = adaptive_frequency
    Setup.update()
    Setup.enable_expression_cache([p_plate, p_coil], "Fields", "Phase=\'0deg\' ", True)

    # solve
    M3D.analyse_nominal()
    M3D.save_project(project_file)

    # Create Icepak project
    IPK = Icepak()
    IPK.copy_solid_bodies_from(M3D)

    IPK.assign_em_losses(M3D.design_name, "MySetupAuto", "LastAdaptive", adaptive_frequency)
    IPK.create_setup("SetupIPK")
    # IPK.insert_ipk_setup("SetupIPK", IPK.GravityDirection.ZNeg, 100, 22, 1e-4, 1e-7)
    airbox = IPK.modeler.primitives.get_obj_id("Region")
    airfaces = IPK.modeler.primitives.get_object_faces(airbox)
    IPK.assign_openings(airfaces)
    IPK.modeler.edit_region_dimensions([])
    IPK.assignmaterial(["Coil_Hole", "Hole"], "air")
    IPK.modeler.primitives["Coil_Hole"].set_model(False)
    IPK.modeler.primitives["Hole"].set_model(False)

    IPK.analyse_nominal()
    IPK.save_project()
    IPK.close_project(IPK.project_name)

pass
