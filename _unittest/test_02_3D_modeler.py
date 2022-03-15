# Setup paths for module imports
from _unittest.conftest import BasisTest
from _unittest.conftest import pyaedt_unittest_check_desktop_error
from pyaedt.application.Design import DesignCache
from pyaedt.modeler.Modeler import FaceCoordinateSystem

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name="Coax_HFSS")
        self.cache = DesignCache(self.aedtapp)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def restore_model(self):
        for name in self.aedtapp.modeler.get_matched_object_name("outer*"):
            self.aedtapp.modeler.delete(name)
        outer = self.aedtapp.modeler.create_cylinder(
            cs_axis="X", position=[0, 0, 0], radius=1, height=20, name="outer", matname="Aluminum"
        )
        for name in self.aedtapp.modeler.get_matched_object_name("Core*"):
            self.aedtapp.modeler.delete(name)
        core = self.aedtapp.modeler.create_cylinder(
            cs_axis="X", position=[0, 0, 0], radius=0.8, height=20, name="Core", matname="teflon_based"
        )
        for name in self.aedtapp.modeler.get_matched_object_name("inner*"):
            self.aedtapp.modeler.delete(name)
        inner = self.aedtapp.modeler.create_cylinder(
            cs_axis="X", position=[0, 0, 0], radius=0.3, height=20, name="inner", matname="Aluminum"
        )

        for name in self.aedtapp.modeler.get_matched_object_name("Poly1*"):
            self.aedtapp.modeler.delete(name)
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [5, 5, 0]
        self.aedtapp.modeler.create_polyline([udp1, udp2, udp3], name="Poly1", xsection_type="Rectangle")

        self.aedtapp.modeler.subtract(outer, core)
        self.aedtapp.modeler.subtract(core, inner)

    @pyaedt_unittest_check_desktop_error
    def test_01_model_units(self):
        self.aedtapp.modeler.model_units = "cm"
        assert self.aedtapp.modeler.model_units == "cm"
        self.restore_model()

    @pyaedt_unittest_check_desktop_error
    def test_02_boundingbox(self):
        bounding = self.aedtapp.modeler.obounding_box
        assert len(bounding) == 6

    @pyaedt_unittest_check_desktop_error
    def test_03_objects(self):
        print(self.aedtapp.modeler.oeditor)
        print(self.aedtapp.modeler._odefinition_manager)
        print(self.aedtapp.modeler._omaterial_manager)

    @pyaedt_unittest_check_desktop_error
    def test_04_convert_to_selection(self):
        assert type(self.aedtapp.modeler.convert_to_selections("inner", True)) is list
        assert type(self.aedtapp.modeler.convert_to_selections("inner", False)) is str

    @pyaedt_unittest_check_desktop_error
    def test_05_split(self):
        box1 = self.aedtapp.modeler.create_box([-10, -10, -10], [20, 20, 20], "box_to_split")
        assert self.aedtapp.modeler.split(box1.name, 2)

    @pyaedt_unittest_check_desktop_error
    def test_06_duplicate_and_mirror(self):
        self.restore_model()
        udp = self.aedtapp.modeler.Position(20, 20, 20)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        out = self.aedtapp.modeler.duplicate_and_mirror("outer", udp, udp2)
        assert out[0]
        assert len(out[1]) > 0

    @pyaedt_unittest_check_desktop_error
    def test_07_mirror(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        status = self.aedtapp.modeler.mirror("outer", udp, udp2)
        assert status

    @pyaedt_unittest_check_desktop_error
    def test_08_duplicate_around_axis(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        num_clones = 3
        status, mirror = self.aedtapp.modeler.duplicate_around_axis("outer", udp, 45, num_clones)
        assert status
        assert type(mirror) is list
        assert len(mirror) == num_clones - 1

    @pyaedt_unittest_check_desktop_error
    def test_08_duplicate_along_line(self):
        udp = self.aedtapp.modeler.Position(5, 5, 5)
        num_clones = 5
        status, mirror = self.aedtapp.modeler.duplicate_along_line("outer", udp, num_clones)
        assert status
        assert type(mirror) is list
        assert len(mirror) == num_clones - 1

    @pyaedt_unittest_check_desktop_error
    def test_09_thicken_sheet(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id5 = self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, udp, 10, name="sheet1")
        udp = self.aedtapp.modeler.Position(100, 100, 100)
        id6 = self.aedtapp.modeler.create_circle(self.aedtapp.PLANE.XY, udp, 10, name="sheet2")
        status = self.aedtapp.modeler.thicken_sheet(id5, 3)
        assert status
        status = self.aedtapp.modeler.automatic_thicken_sheets(id6, 3, False)
        assert status

    @pyaedt_unittest_check_desktop_error
    def test_11_split(self):
        self.restore_model()
        assert self.aedtapp.modeler.split(
            "Poly1",
            self.aedtapp.PLANE.XY,
        )

    def test_12_separate_Bodies(self):
        assert self.aedtapp.modeler.separate_bodies("Poly1")

    def test_13_rotate(self):
        assert self.aedtapp.modeler.rotate("Poly1", self.aedtapp.AXIS.X, 30)

    def test_14_subtract(self):
        o1 = self.aedtapp.modeler["outer"].clone()
        o2 = self.aedtapp.modeler["inner"].clone()
        assert self.aedtapp.modeler.subtract(o1, o2)

    def test_15_purge_history(self):
        o1 = self.aedtapp.modeler["outer"].clone()
        o2 = self.aedtapp.modeler["inner"].clone()
        assert self.aedtapp.modeler.purge_history([o1, o2])

    def test_16_get_model_bounding_box(self):
        assert len(self.aedtapp.modeler.get_model_bounding_box()) == 6

    def test_17_unite(self):
        o1 = self.aedtapp.modeler["outer"].clone()
        o2 = self.aedtapp.modeler["inner"].clone()
        assert self.aedtapp.modeler.unite([o1, o2])

    def test_18_chamfer(self):
        # TODO
        assert True

    def test_19_clone(self):
        self.restore_model()
        status, cloned = self.aedtapp.modeler.clone("Poly1")
        assert status

    def test_20_intersect(self):
        udp = [0, 0, 0]
        o1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [5, 10], name="Rect1")
        o2 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [3, 12], name="Rect2")
        assert self.aedtapp.modeler.intersect([o1, o2])

    def test_21_connect(self):
        udp = [0, 0, 0]
        id1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [5, 10])
        udp = self.aedtapp.modeler.Position(0, 0, 10)
        id2 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [-3, 10])
        assert self.aedtapp.modeler.connect([id1, id2])

    def test_22_translate(self):
        udp = [0, 0, 0]
        id1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [5, 10])
        id2 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, udp, [3, 12])
        udp2 = self.aedtapp.modeler.Position(0, 20, 5)
        assert self.aedtapp.modeler.translate([id1, id2], udp2)

    def test_23_chassis_subtraction(self):
        # TODO
        assert True

    def test_24_check_plane(self):

        udp = [0, 0, 0]
        o1 = self.aedtapp.modeler.create_box(udp, [4, 5, 5])
        plane = self.aedtapp.modeler.check_plane(o1.id, udp)
        planes = ["XY", "XZ", "YZ"]
        assert plane in planes

    def test_25_clean_object_name(self):
        # TODO
        assert True

    def test_26_create_airbox(self):
        o1 = self.aedtapp.modeler.create_airbox(10)
        o2 = self.aedtapp.modeler.create_airbox(50, "Relative", "Second_airbox")
        assert o1.id > 0
        assert o2.id > 0

    def test_27_create_region(self):
        assert self.aedtapp.modeler.create_air_region(*[20, 20, 30, 50, 50, 100])
        assert self.aedtapp.modeler.edit_region_dimensions([40, 30, 30, 50, 50, 100])

    def test_28_create_face_list(self):
        fl = self.aedtapp.modeler.get_object_faces("Second_airbox")
        assert self.aedtapp.modeler.create_face_list(fl, "my_face_list")

    def test_28B_create_object_list(self):
        assert self.aedtapp.modeler.create_object_list(["Second_airbox"], "my_object_list")

    def test_29_create_outer_face_list(self):
        assert self.aedtapp.modeler.create_outer_facelist(["Second_airbox"])

    def test_30_create_waveguide(self):
        position = self.aedtapp.modeler.Position(0, 0, 0)
        wg1 = self.aedtapp.modeler.create_waveguide(position, self.aedtapp.AXIS.X, wg_length=2000)
        assert isinstance(wg1, tuple)
        position = self.aedtapp.modeler.Position(0, 0, 0)
        wg9 = self.aedtapp.modeler.create_waveguide(
            position,
            self.aedtapp.AXIS.Z,
            wgmodel="WG9",
            wg_length=1500,
            parametrize_h=True,
            create_sheets_on_openings=True,
        )
        assert wg9[0].id > 0
        assert wg9[1].id > 0
        assert wg9[2].id > 0
        wgfail = self.aedtapp.modeler.create_waveguide(
            position, self.aedtapp.AXIS.Z, wgmodel="MYMODEL", wg_length=2000, parametrize_h=True
        )
        assert not wgfail
        pass

    def test_31_set_objects_unmodel(self):
        assert self.aedtapp.modeler.set_object_model_state("Second_airbox", False)

    def test_33_duplicate_around_axis(self):
        id1 = self.aedtapp.modeler.create_box([10, 10, 10], [4, 5, 5])
        axis = self.aedtapp.AXIS.X
        _, obj_list = self.aedtapp.modeler.duplicate_around_axis(
            id1, cs_axis=axis, angle="180deg", nclones=2, create_new_objects=False
        )
        # if create_new_objects is set to False, there should be no new objects
        assert not obj_list

    def test_35_activate_variable_for_tuning(self):
        self.aedtapp["test_opti"] = "10mm"
        self.aedtapp["$test_opti1"] = "10mm"
        assert self.aedtapp.activate_variable_tuning("test_opti")
        assert self.aedtapp.activate_variable_tuning("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_tuning("test_opti")

    def test_36_activate_variable_for_optimization(self):
        assert self.aedtapp.activate_variable_optimization("test_opti")
        assert self.aedtapp.activate_variable_optimization("$test_opti1", "2mm", "5mm")
        assert self.aedtapp.deactivate_variable_optimization("test_opti")

    def test_37_activate_variable_for_sensitivity(self):

        assert self.aedtapp.activate_variable_sensitivity("test_opti")
        assert self.aedtapp.activate_variable_sensitivity("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_sensitivity("$test_opti1")

    def test_38_activate_variable_for_statistical(self):

        assert self.aedtapp.activate_variable_statistical("test_opti")
        assert self.aedtapp.activate_variable_statistical("$test_opti1", "1mm", "10mm", "3%", mean="2mm")
        assert self.aedtapp.deactivate_variable_statistical("test_opti")

    def test_39_create_coaxial(self):
        coax = self.aedtapp.modeler.create_coaxial([0, 0, 0], self.aedtapp.AXIS.X)
        assert isinstance(coax[0].id, int)
        assert isinstance(coax[1].id, int)
        assert isinstance(coax[2].id, int)

    def test_40_create_coordinate_system(self):
        cs = self.aedtapp.modeler.create_coordinate_system()
        assert cs
        assert cs.update()
        assert cs.change_cs_mode(1)
        assert cs.change_cs_mode(2)

        try:
            cs.change_cs_mode(3)
            assert False
        except ValueError:
            pass

        assert cs.change_cs_mode(0)
        assert cs.delete()

    def test_40a_create_face_coordinate_system(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [2, 2, 2])
        face = box.faces[0]
        fcs = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[0], face.edges[1])
        assert fcs
        assert fcs.face_id == face.id
        assert fcs.update()
        assert fcs.delete()
        fcs2 = self.aedtapp.modeler.create_face_coordinate_system(face, face, face.edges[1].vertices[0])
        assert fcs2
        assert fcs2.delete()
        fcs2 = self.aedtapp.modeler.create_face_coordinate_system(
            face, face.edges[0].vertices[0], face.edges[1].vertices[0]
        )
        assert fcs2
        assert fcs2.delete()
        fcs3 = self.aedtapp.modeler.create_face_coordinate_system(
            face, face.edges[1].vertices[1], face.edges[1].vertices[0]
        )
        assert fcs3
        assert fcs3.delete()
        fcs4 = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[2], face.edges[3], name="test")
        assert fcs4
        assert fcs4.name == "test"
        assert fcs4.delete()
        fcs5 = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[2], face.edges[3], axis="Y")
        assert fcs5
        assert fcs5.props["WhichAxis"] == "Y"
        assert fcs5.delete()
        fcs6 = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[2], face.edges[3], rotation=14.3)
        assert fcs6
        assert fcs6.props["ZRotationAngle"] == "14.3deg"
        assert fcs6.delete()
        fcs7 = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[2], face.edges[3], offset=[0.2, 0.3])
        assert fcs7
        assert fcs7.props["XOffset"] == "0.2" + self.aedtapp.modeler.model_units
        assert fcs7.props["YOffset"] == "0.3" + self.aedtapp.modeler.model_units
        assert fcs7.delete()
        fcs8 = self.aedtapp.modeler.create_face_coordinate_system(face.id, face.edges[0].id, face.edges[1].id)
        assert fcs8
        assert fcs8.delete()
        fcs9 = self.aedtapp.modeler.create_face_coordinate_system(face.id, face.edges[0].vertices[0].id, face.id)
        assert fcs9
        assert fcs9.delete()
        fcs10 = self.aedtapp.modeler.create_face_coordinate_system(
            face, face.edges[2], face.edges[3], always_move_to_end=False
        )
        assert fcs10
        assert fcs10.props["MoveToEnd"] is False
        assert fcs10.delete()
        fcs = FaceCoordinateSystem(self.aedtapp.modeler)
        assert fcs._part_name is None
        assert fcs._get_type_from_id(box.id) == "3dObject"
        assert fcs._get_type_from_id(face.id) == "Face"
        assert fcs._get_type_from_id(face.edges[0].id) == "Edge"
        assert fcs._get_type_from_id(face.edges[0].vertices[0].id) == "Vertex"
        assert fcs._get_type_from_object(box) == "3dObject"
        assert fcs._get_type_from_object(face) == "Face"
        assert fcs._get_type_from_object(face.edges[0]) == "Edge"
        assert fcs._get_type_from_object(face.edges[0].vertices[0]) == "Vertex"

    def test_41_rename_coordinate(self):
        cs = self.aedtapp.modeler.create_coordinate_system(name="oldname")
        assert cs.name == "oldname"
        assert cs.rename("newname")
        assert cs.name == "newname"
        assert cs.delete()

    def test_41a_rename_face_coordinate(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [2, 2, 2])
        face = box.faces[0]
        fcs = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[0], face.edges[1], name="oldname")
        assert fcs.name == "oldname"
        assert fcs.rename("newname")
        assert fcs.name == "newname"
        assert fcs.delete()

    def test_42A_update_coordinate_system(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="CS1", view="rotate")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="CS2", mode="view", view="iso")
        cs2.ref_cs = "CS1"
        assert cs2.update()
        cs1.props["OriginX"] = 10
        cs1.props["OriginY"] = 10
        cs1.props["OriginZ"] = 10
        assert cs1.update()
        assert cs2.change_cs_mode(2)
        cs2.props["Phi"] = 30
        cs2.props["Theta"] = 30
        assert cs2.update()
        cs2.ref_cs = "Global"
        assert cs2.update()
        assert tuple(self.aedtapp.modeler.oeditor.GetCoordinateSystems()) == ("Global", "CS1", "CS2")
        assert len(self.aedtapp.modeler.coordinate_systems) == 2
        assert cs2.delete()

    def test_42A_update_face_coordinate_system(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        box = self.aedtapp.modeler.create_box([0, 0, 0], [2, 2, 2])
        face = box.faces[0]
        fcs = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[0], face.edges[1], name="FCS1")
        assert fcs
        fcs.props["XOffset"] = "0.2mm"
        fcs.props["YOffset"] = "0.3mm"
        assert fcs.props["XOffset"] == "0.2mm"
        assert fcs.props["YOffset"] == "0.3mm"
        assert fcs.update()
        fcs.props["ZRotationAngle"] = "14.3deg"
        assert fcs.update()
        assert fcs.props["ZRotationAngle"] == "14.3deg"
        fcs.props["WhichAxis"] = "Y"
        assert fcs.update()
        assert fcs.props["WhichAxis"] == "Y"
        fcs.props["MoveToEnd"] = False
        assert fcs.update()
        assert fcs.props["MoveToEnd"] is False
        assert tuple(self.aedtapp.modeler.oeditor.GetCoordinateSystems()) == ("Global", "FCS1")
        assert len(self.aedtapp.modeler.coordinate_systems) == 1
        assert fcs.delete()

    def test_42B_set_as_working_cs(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="first")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="second", mode="view", view="iso")
        assert cs1.set_as_working_cs()
        assert cs2.set_as_working_cs()

    def test_42C_set_as_working_face_cs(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        box = self.aedtapp.modeler.create_box([0, 0, 0], [2, 2, 2])
        face = box.faces[0]
        fcs1 = self.aedtapp.modeler.create_face_coordinate_system(face, face.edges[0], face.edges[1])
        fcs2 = self.aedtapp.modeler.create_face_coordinate_system(face, face, face.edges[1])
        assert fcs1.set_as_working_cs()
        assert fcs2.set_as_working_cs()

    def test_43_set_working_coordinate_system(self):
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="new1")
        assert self.aedtapp.modeler.set_working_coordinate_system("Global")
        assert self.aedtapp.modeler.set_working_coordinate_system("new1")
        assert self.aedtapp.modeler.set_working_coordinate_system("Global")
        assert self.aedtapp.modeler.set_working_coordinate_system(cs1)

    def test_43_set_working_face_coordinate_system(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [2, 2, 2])
        face = box.faces[0]
        fcs = self.aedtapp.modeler.create_face_coordinate_system(face, face, face.edges[1], name="new2")
        assert self.aedtapp.modeler.set_working_coordinate_system("Global")
        assert self.aedtapp.modeler.set_working_coordinate_system("new2")
        assert self.aedtapp.modeler.set_working_coordinate_system("Global")
        assert self.aedtapp.modeler.set_working_coordinate_system(fcs)

    def test_44_sweep_around_axis(self):
        rect1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.YZ, [0, 0, 0], [20, 20], "rectangle_to_split")
        assert rect1.sweep_around_axis("Z", sweep_angle=360, draft_angle=0)

    def test_45_sweep_along_path(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        path = self.aedtapp.modeler.create_polyline([udp1, udp2], name="Poly1")
        rect1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.YZ, [0, 0, 0], [20, 20], "rectangle_to_sweep")
        assert rect1.sweep_along_path(path)

    def test_46_section_object(self):
        box1 = self.aedtapp.modeler.create_box([-10, -10, -10], [20, 20, 20], "box_to_split")
        assert self.aedtapp.modeler.section(box1, 0, create_new=True, section_cross_object=False)
        pass

    def test_47_sweep_along_vector(self):
        sweep_vector = [5, 0, 0]
        rect1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.YZ, [0, 0, 0], [20, 20], "rectangle_to_vector")
        assert rect1.sweep_along_vector(sweep_vector)

    def test_48_coordinate_systems_parametric(self):
        self.aedtapp["var1"] = "5mm"
        self.aedtapp["var2"] = "(3mm+var1)*2"
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="CSP1", mode="axis", x_pointing=["var1", "var2", 0])
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="CSP2", mode="axis", x_pointing=["5mm", "16mm", 0])
        assert cs1.quaternion == cs2.quaternion

        self.aedtapp["var3"] = "43deg"
        self.aedtapp["var4"] = "(20deg+var3)*2"
        cs3 = self.aedtapp.modeler.create_coordinate_system(name="CSP3", mode="zxz", phi="var3", theta="var4", psi=0)
        cs4 = self.aedtapp.modeler.create_coordinate_system(name="CSP4", mode="zxz", phi=43, theta="126deg", psi=0)
        tol = 1e-9
        assert sum([abs(x1 - x2) for (x1, x2) in zip(cs3.quaternion, cs4.quaternion)]) < tol
