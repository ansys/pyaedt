# standard imports
import os
import pytest
# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
import gc
test_project_name = "Coax_HFSS"


class TestModeler:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                self.test_project = self.local_scratch.copyfile(example_project)

                self.aedtapp = Hfss(self.test_project)
            except Exception as e:
                # self.desktop.force_close_desktop()
                print(e)

    def teardown_class(self):
        self.aedtapp.close_project(self.aedtapp.project_name)
        # self.desktop.force_close_desktop()
        self.local_scratch.remove()
        gc.collect()

    def test_01_model_units(self):
        model_units = self.aedtapp.modeler.model_units
        self.aedtapp.modeler.model_units = "cm"
        assert self.aedtapp.modeler.model_units == "cm"

    def test_01b_load_material_lib(self):
        filename = os.path.join(local_path, "example_models", "amat.xml")
        mats = self.aedtapp.materials.load_from_xml_full(filename)
        assert mats != {}
        assert mats is not None

    def test_01c_load_material_lib(self):
        filename = os.path.join(local_path, "example_models", "amat.xml")
        assert self.aedtapp.materials.load_from_file(filename)

    def test_01c_export_material_lib(self):
        self.aedtapp.materials.py2xmlFull(os.path.join(self.local_scratch.path,"export.xml"))
        assert os.path.exists(os.path.join(self.local_scratch.path,"export.xml"))

    def test_02_boundingbox(self):
        bounding = self.aedtapp.modeler.obounding_box
        assert len(bounding) == 6

    def test_03_objects(self):
        try:
            print(self.aedtapp.modeler.oeditor)
            print(self.aedtapp.modeler.odefinition_manager)
            print(self.aedtapp.modeler.omaterial_manager)
        except:
            assert False

    def test_04_convert_to_selection(self):
        assert type(self.aedtapp.modeler.convert_to_selections("inner", True)) is list
        assert type(self.aedtapp.modeler.convert_to_selections("inner", False)) is str

    def test_05_split(self):
        box1 = self.aedtapp.modeler.primitives.create_box([-10, -10, -10], [20, 20, 20], "box_to_split")
        assert self.aedtapp.modeler.split("box_to_split", 1)

    def test_06_duplicate_and_mirror(self):
        udp = self.aedtapp.modeler.Position(20, 20, 20)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        out = self.aedtapp.modeler.duplicate_and_mirror("outer", udp, udp2)
        assert out[0]

    def test_07_mirror(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(30, 40, 40)
        status = self.aedtapp.modeler.mirror("outer", udp, udp2)
        assert status

    def test_08_duplicate_around_axis(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        status, mirror = self.aedtapp.modeler.duplicate_around_axis("outer", udp, 45, 3)
        assert status
        assert type(mirror) is list

    def test_08_duplicate_along_line(self):
        udp = self.aedtapp.modeler.Position(5, 5, 5)
        status, mirror = self.aedtapp.modeler.duplicate_along_line("outer", udp, 5)
        assert status
        assert type(mirror) is list

    def test_09_thicken_sheet(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id5 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10,
                                                            name="sheet1")
        udp = self.aedtapp.modeler.Position(100, 100, 100)
        id6 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10,
                                                            name="sheet2")
        status = self.aedtapp.modeler.thicken_sheet(id5, 3)
        assert status
        status = self.aedtapp.modeler.automatic_thicken_sheets(id6, 3, False)
        assert status

    def test_11_split(self):
        udp1 = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(5, 0, 0)
        udp3 = self.aedtapp.modeler.Position(5, 5, 0)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3]
        id5 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly1", xsection_type="Rectangle")
        assert self.aedtapp.modeler.split("Poly1", self.aedtapp.CoordinateSystemPlane.XYPlane, )

    def test_12_separate_Bodies(self):
        assert self.aedtapp.modeler.separate_bodies("Poly1")

    def test_13_rotate(self):
        assert self.aedtapp.modeler.rotate("Poly1", self.aedtapp.CoordinateSystemAxis.XAxis, 30)

    def test_14_subtract(self):
        assert self.aedtapp.modeler.subtract("outer_1", "outer_2")

    def test_15_purge_history(self):
        assert self.aedtapp.modeler.purge_history(["outer_3", "outer_4"])

    def test_16_get_model_bounding_box(self):
        assert len(self.aedtapp.modeler.get_model_bounding_box()) == 6

    def test_17_unite(self):
        assert self.aedtapp.modeler.unite(["outer_5", "outer_6"])

    def test_18_chamfer(self):
        # TODO
        assert True

    def test_19_clone(self):
        status, cloned = self.aedtapp.modeler.clone("Poly1")
        assert status
        assert type(cloned) is str

    def test_20_intersect(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10],
                                                               name="Rect1")
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [3, 12],
                                                               name="Rect2")
        assert self.aedtapp.modeler.intersect([id1, id2])

    def test_21_connect(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10])
        udp = self.aedtapp.modeler.Position(0, 0, 10)
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp,
                                                               [-3, 10])
        assert self.aedtapp.modeler.connect([id1, id2])

    def test_22_translate(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [5, 10])
        id2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, [3, 12])
        udp2 = self.aedtapp.modeler.Position(0, 20, 5)
        assert self.aedtapp.modeler.translate([id1, id2], udp2)

    def test_23_chassis_subtraction(self):
        # TODO
        assert True

    def test_24_check_plane(self):

        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id1 = self.aedtapp.modeler.primitives.create_box(udp, [4, 5, 5])
        plane = self.aedtapp.modeler.check_plane(id1, udp)
        planes = ["XY", "XZ", "YZ"]
        assert plane in planes

    def test_25_clean_object_name(self):
        # TODO
        assert True

    def test_26_create_airbox(self):
        id = self.aedtapp.modeler.create_airbox(10)
        id2 = self.aedtapp.modeler.create_airbox(50, "Relative", "Second_airbox")
        assert type(id) is int
        assert type(id2) is int

    def test_27_create_region(self):
        assert self.aedtapp.modeler.create_air_region(*[20, 20, 30, 50, 50, 100])
        assert self.aedtapp.modeler.edit_region_dimensions([40, 30, 30, 50, 50, 100])

    def test_28_create_face_list(self):
        fl = self.aedtapp.modeler.primitives.get_object_faces("Second_airbox")
        assert self.aedtapp.modeler.create_face_list(fl, "my_face_list")

    def test_28B_create_object_list(self):
        assert self.aedtapp.modeler.create_object_list(["Second_airbox"], "my_object_list")

    def test_29_create_outer_face_list(self):
        assert self.aedtapp.modeler.create_outer_facelist(["Second_airbox"])

    def test_30_create_waveguide(self):
        position = self.aedtapp.modeler.Position(0, 0, 0)
        assert type(self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.XAxis,
                                                          wg_length=2000)) is tuple
        position = self.aedtapp.modeler.Position(0, 0, 0)
        wg9 = self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.ZAxis, wgmodel="WG9",
                                                    wg_length=1500, parametrize_h=True, create_sheets_on_openings=True)
        assert wg9[0] > 0
        assert wg9[1] > 0
        assert wg9[2] > 0
        wgfail = self.aedtapp.modeler.create_waveguide(position, self.aedtapp.CoordinateSystemAxis.ZAxis,
                                                       wgmodel="MYMODEL",
                                                       wg_length=2000, parametrize_h=True)
        assert wgfail == None
        pass

    def test_31_set_objects_unmodel(self):
        assert self.aedtapp.modeler.set_object_model_state("Second_airbox", False)

    def test_32_get_object_bounding_box(self):
        id1 = self.aedtapp.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        my_pos = self.aedtapp.modeler.get_object_bounding_box(id1)
        assert ((my_pos[0] + my_pos[1] + my_pos[2] - 30) < 1e-5)

    def test_33_duplicate_around_axis(self):
        id1 = self.aedtapp.modeler.primitives.create_box([10, 10, 10], [4, 5, 5])
        axis = self.aedtapp.CoordinateSystemAxis.XAxis
        _, obj_list = self.aedtapp.modeler.duplicate_around_axis(id1, cs_axis=axis, angle="180deg", nclones=2,
                                                                 create_new_objects=False)
        # if create_new_objects is set to False, there should be no new objects
        assert not obj_list

    def test_35_activate_variable_for_tuning(self):
        self.aedtapp["test_opti"]="10mm"
        self.aedtapp["$test_opti1"]="10mm"
        assert self.aedtapp.activate_variable_tuning("test_opti")
        assert self.aedtapp.activate_variable_tuning("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_tuning("test_opti")

    def test_36_activate_variable_for_optimization(self):
        assert self.aedtapp.activate_variable_optimization("test_opti")
        assert self.aedtapp.activate_variable_optimization("$test_opti1", "2mm", "5mm")
        assert self.aedtapp.deactivate_variable_optimization("test_opti")

    def test_35_activate_variable_for_sensitivity(self):

        assert self.aedtapp.activate_variable_sensitivity("test_opti")
        assert self.aedtapp.activate_variable_sensitivity("$test_opti1", "1mm", "10mm")
        assert self.aedtapp.deactivate_variable_sensitivity("$test_opti1")

    def test_35_activate_variable_for_statistical(self):

        assert self.aedtapp.activate_variable_statistical("test_opti")
        assert self.aedtapp.activate_variable_statistical("$test_opti1", "1mm", "10mm", "3%", mean="2mm")
        assert self.aedtapp.deactivate_variable_statistical("test_opti")

    def test_36_create_coaxial(self):
        coax = self.aedtapp.modeler.create_coaxial([0, 0, 0], self.aedtapp.CoordinateSystemAxis.XAxis)
        assert isinstance(coax[0], int)
        assert isinstance(coax[1], int)
        assert isinstance(coax[2], int)

    def test_37_create_coordinate(self):
        cs = self.aedtapp.modeler.create_coordinate_system()
        assert cs
        assert cs.update()
        assert cs.change_cs_mode(1)
        assert cs.change_cs_mode(2)
        assert not cs.change_cs_mode(3)
        assert cs.change_cs_mode(0)
        assert cs.delete()

    def test_38_rename_coordinate(self):
        cs = self.aedtapp.modeler.create_coordinate_system(name='oldname')
        assert cs.name == 'oldname'
        assert cs.rename('newname')
        assert cs.name == 'newname'

    def test_39_update_coordinate_system(self):
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
        cs2.update()
        assert self.aedtapp.modeler.oeditor.GetCoordinateSystems() == ('Global', 'CS1', 'CS2')
        assert len(self.aedtapp.modeler.coordinate_systems) == 2
        assert cs2.delete()

    def test_40_set_as_working_cs(self):
        for cs in self.aedtapp.modeler.coordinate_systems:
            cs.delete()
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="first")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="second", mode="view", view="iso")
        assert cs1.set_as_working_cs()
        assert cs2.set_as_working_cs()

    def test_41_set_working_coordinate_system(self):
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="new1")
        self.aedtapp.modeler.set_working_coordinate_system("Global")
        self.aedtapp.modeler.set_working_coordinate_system("new1")

