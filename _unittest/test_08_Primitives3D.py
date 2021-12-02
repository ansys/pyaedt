# standard imports
import os
import sys
import time
import gc

try:
    import pytest
except:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import scratch_path, local_path, BasisTest, pyaedt_unittest_check_desktop_error, config
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.filesystem import Scratch
from pyaedt.modeler.Primitives import Polyline, PolylineSegment
from pyaedt.modeler.Object3d import Object3d
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.generic.constants import AXIS

test = sys.modules.keys()

scdoc = "input.scdoc"
step = "input.stp"


class TestClass(BasisTest):
    def setup_class(self):
        gc.collect()
        BasisTest.setup_class(self, project_name="test_primitives", design_name="3D_Primitives")
        with Scratch(scratch_path) as self.local_scratch:
            scdoc_file = os.path.join(local_path, "example_models", scdoc)
            self.local_scratch.copyfile(scdoc_file)
            self.step_file = os.path.join(local_path, "example_models", step)
            test_98_project = os.path.join(local_path, "example_models", "assembly2" + ".aedt")
            self.test_98_project = self.local_scratch.copyfile(test_98_project)
            test_99_project = os.path.join(local_path, "example_models", "assembly" + ".aedt")
            self.test_99_project = self.local_scratch.copyfile(test_99_project)

    def create_copper_box(self, name=None):
        if not name:
            name = "MyBox"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        else:
            pass
        new_object = self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
        return new_object

    def create_copper_sphere(self, name=None):
        if not name:
            name = "Mysphere"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        return self.aedtapp.modeler.primitives.create_sphere([0, 0, 0], radius="1mm", name=name, matname="Copper")

    def create_copper_cylinder(self, name=None):
        if not name:
            name = "MyCyl"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        return self.aedtapp.modeler.primitives.create_cylinder(
            cs_axis="Y", position=[20, 20, 0], radius=5, height=20, numSides=8, name=name, matname="Copper"
        )

    def create_rectangle(self, name=None):
        if not name:
            name = "MyRectangle"
        if self.aedtapp.modeler.primitives[name]:
            self.aedtapp.modeler.primitives.delete(name)
        plane = self.aedtapp.PLANE.XY
        return self.aedtapp.modeler.primitives.create_rectangle(plane, [5, 3, 8], [4, 5], name=name)

    def create_polylines(self, name=None):
        if not name:
            name = "Poly_"

        test_points = [[0, 100, 0], [-100, 0, 0], [-50, -50, 0], [0, 0, 0]]

        if self.aedtapp.modeler.primitives[name + "segmented"]:
            self.aedtapp.modeler.primitives.delete(name + "segmented")

        if self.aedtapp.modeler.primitives[name + "compound"]:
            self.aedtapp.modeler.primitives.delete(name + "compound")

        p1 = self.aedtapp.modeler.primitives.create_polyline(position_list=test_points, name=name + "segmented")
        p2 = self.aedtapp.modeler.primitives.create_polyline(
            position_list=test_points, segment_type=["Line", "Arc"], name=name + "compound"
        )
        return p1, p2, test_points

    @pyaedt_unittest_check_desktop_error
    def test_01_resolve_object(self):
        o = self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 5], "MyCreatedBox", "Copper")
        o1 = self.aedtapp.modeler.primitives._resolve_object(o)
        o2 = self.aedtapp.modeler.primitives._resolve_object(o.id)
        o3 = self.aedtapp.modeler.primitives._resolve_object(o.name)

        assert isinstance(o1, Object3d)
        assert isinstance(o2, Object3d)
        assert isinstance(o3, Object3d)
        assert o1.id == o.id
        assert o2.id == o.id
        assert o3.id == o.id
        self.cache.ignore_error_message_local("Error. Object")
        oinvalid1 = self.aedtapp.modeler.primitives._resolve_object(-1)
        oinvalid2 = self.aedtapp.modeler.primitives._resolve_object("FrankInvalid")
        assert not oinvalid1
        assert not oinvalid2

    @pyaedt_unittest_check_desktop_error
    def test_02_create_box(self):
        o = self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 5], "MyCreatedBox_11", "Copper")
        assert o.id > 0
        assert o.name.startswith("MyCreatedBox_11")
        assert o.object_type == "Solid"
        assert o.is3d == True
        assert o.material_name == "copper"
        assert "MyCreatedBox_11" in self.aedtapp.modeler.primitives.solid_names
        assert len(self.aedtapp.modeler.primitives.object_names) == len(self.aedtapp.modeler.primitives.objects)

    @pyaedt_unittest_check_desktop_error
    def test_03_create_box_assertions(self):
        try:
            invalid_entry = "Frank"
            self.aedtapp.modeler.primitives.create_box([0, 0, 0], invalid_entry, "MyCreatedBox", "Copper")
            assert False
        except AssertionError:
            pass

    @pyaedt_unittest_check_desktop_error
    def test_04_create_polyhedron(self):

        o1 = self.aedtapp.modeler.primitives.create_polyhedron()
        assert o1.id > 0
        assert o1.name.startswith("New")
        assert o1.object_type == "Solid"
        assert o1.is3d == True
        assert o1.material_name == "vacuum"
        assert o1.solve_inside

        o2 = self.aedtapp.modeler.primitives.create_polyhedron(
            cs_axis=AXIS.Z,
            center_position=[0, 0, 0],
            start_position=[0, 1, 0],
            height=2.0,
            num_sides=5,
            name="MyPolyhedron",
            matname="Aluminum",
        )
        assert o2.id > 0
        assert o2.object_type == "Solid"
        assert o2.is3d == True
        assert o2.material_name == "aluminum"
        assert o2.solve_inside == False

        assert o1.name in self.aedtapp.modeler.primitives.solid_names
        assert o2.name in self.aedtapp.modeler.primitives.solid_names
        assert len(self.aedtapp.modeler.primitives.object_names) == len(self.aedtapp.modeler.primitives.objects)
        pass

    @pyaedt_unittest_check_desktop_error
    def test_05_center_and_centroid(self):
        o = self.create_copper_box()
        tol = 1e-9
        assert GeometryOperators.v_norm(o.faces[0].center_from_aedt) - GeometryOperators.v_norm(o.faces[0].center) < tol

    @pyaedt_unittest_check_desktop_error
    def test_11_get_object_name_from_edge(self):
        o = self.create_copper_box()
        edge = o.edges[0].id
        assert self.aedtapp.modeler.get_object_name_from_edge_id(edge) == o.name

        udp = self.aedtapp.modeler.Position(0, 0, 0)
        dimensions = [10, 10, 5]
        o = self.aedtapp.modeler.primitives.create_box(udp, dimensions)
        assert len(o.name) == 16
        assert o.material_name == "vacuum"

    @pyaedt_unittest_check_desktop_error
    def test_11a_get_faces_from_mat(self):
        self.create_copper_box()
        faces = self.aedtapp.modeler.get_faces_from_materials("Copper")
        assert len(faces) >= 6

    @pyaedt_unittest_check_desktop_error
    def test_11b_check_object_faces(self):
        o = self.create_copper_box()
        face_list = o.faces
        assert len(face_list) == 6
        f = o.faces[0]
        assert isinstance(f.center, list) and len(f.center) == 3
        assert isinstance(f.area, float) and f.area > 0
        assert o.faces[0].move_with_offset(0.1)
        assert o.faces[0].move_with_vector([0, 0, 0.01])
        assert type(f.normal) is list

    @pyaedt_unittest_check_desktop_error
    def test_11c_check_object_edges(self):
        o = self.create_copper_box(name="MyBox")
        e = o.edges[1]
        assert isinstance(e.midpoint, list) and len(e.midpoint) == 3
        assert isinstance(e.length, float) and e.length > 0

    @pyaedt_unittest_check_desktop_error
    def test_11d_check_object_vertices(self):
        o = self.create_copper_box(name="MyBox")
        assert len(o.vertices) == 8
        v = o.vertices[0]
        assert isinstance(v.position, list) and len(v.position) == 3

    @pyaedt_unittest_check_desktop_error
    def test_12_get_objects_in_group(self):
        objs = self.aedtapp.modeler.get_objects_in_group("Solids")
        assert type(objs) is list

    @pyaedt_unittest_check_desktop_error
    def test_13_create_circle(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.PLANE.XY
        o = self.aedtapp.modeler.primitives.create_circle(plane, udp, 2, name="MyCircle", matname="Copper")
        assert o.id > 0
        assert o.name.startswith("MyCircle")
        assert o.object_type == "Sheet"
        assert o.is3d is False
        assert not o.solve_inside

    @pyaedt_unittest_check_desktop_error
    def test_14_create_sphere(self):
        udp = self.aedtapp.modeler.Position(20, 20, 0)
        radius = 5
        o = self.aedtapp.modeler.primitives.create_sphere(udp, radius, "MySphere", "Copper")
        assert o.id > 0
        assert o.name.startswith("MySphere")
        assert o.object_type == "Solid"
        assert o.is3d is True

    @pyaedt_unittest_check_desktop_error
    def test_15_create_cylinder(self):
        udp = self.aedtapp.modeler.Position(20, 20, 0)
        axis = self.aedtapp.AXIS.Y
        radius = 5
        height = 50
        o = self.aedtapp.modeler.primitives.create_cylinder(axis, udp, radius, height, 8, "MyCyl", "Copper")
        assert o.id > 0
        assert o.name.startswith("MyCyl")
        assert o.object_type == "Solid"
        assert o.is3d is True
        pass

    @pyaedt_unittest_check_desktop_error
    def test_16_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.PLANE.XY
        o1 = self.aedtapp.modeler.primitives.create_ellipse(
            plane, udp, 5, 1.5, True, name="MyEllpise01", matname="Copper"
        )
        assert o1.id > 0
        assert o1.name.startswith("MyEllpise01")
        assert o1.object_type == "Sheet"
        assert o1.is3d is False
        assert not o1.solve_inside

        o2 = self.aedtapp.modeler.primitives.create_ellipse(
            plane, udp, 5, 1.5, True, name="MyEllpise01", matname="Vacuum"
        )
        assert o2.id > 0
        assert o2.name.startswith("MyEllpise01")
        assert o2.object_type == "Sheet"
        assert o2.is3d is False
        assert not o2.solve_inside

        o3 = self.aedtapp.modeler.primitives.create_ellipse(plane, udp, 5, 1.5, False, name="MyEllpise02")
        assert o3.id > 0
        assert o3.name.startswith("MyEllpise02")
        assert o3.object_type == "Line"
        assert o3.is3d is False
        assert not o3.solve_inside

    @pyaedt_unittest_check_desktop_error
    def test_17_create_object_from_edge(self):
        o = self.create_copper_cylinder()
        edges = o.edges
        o = self.aedtapp.modeler.primitives.create_object_from_edge(edges[0])
        assert o.id > 0
        assert o.object_type == "Line"
        assert o.is3d is False
        pass

    @pyaedt_unittest_check_desktop_error
    def test_18_create_object_from_face(self):
        o = self.create_copper_cylinder()
        faces = o.faces
        o = self.aedtapp.modeler.primitives.create_object_from_face(faces[0])
        assert o.id > 0
        assert o.object_type == "Sheet"
        assert o.is3d is False
        pass

    @pyaedt_unittest_check_desktop_error
    def test_19_create_polyline(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [5, 5, 0]
        udp4 = [2, 5, 3]
        arrofpos = [udp1, udp4, udp2, udp3, udp1]
        P = self.aedtapp.modeler.primitives.create_polyline(
            arrofpos, cover_surface=True, name="Poly1", matname="Copper"
        )
        assert isinstance(P, Polyline)
        assert isinstance(P, Object3d)
        assert P.object_type == "Sheet"
        assert P.is3d == False
        assert isinstance(P.color, tuple)
        get_P = self.aedtapp.modeler.primitives["Poly1"]
        assert isinstance(get_P, Polyline)

    @pyaedt_unittest_check_desktop_error
    def test_20_create_polyline_with_crosssection(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [5, 5, 0]
        udp4 = [2, 5, 3]
        arrofpos = [udp1, udp2, udp3]
        P = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly_xsection", xsection_type="Rectangle")
        assert isinstance(P, Polyline)
        assert self.aedtapp.modeler.primitives[P.id].object_type == "Solid"
        assert self.aedtapp.modeler.primitives[P.id].is3d == True

    @pyaedt_unittest_check_desktop_error
    def test_21_sweep_along_path(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [5, 5, 0]
        arrofpos = [udp1, udp2, udp3]
        path = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector")
        my_name = path.name
        assert my_name in self.aedtapp.modeler.primitives.line_names
        assert my_name in self.aedtapp.modeler.primitives.model_objects
        assert my_name in self.aedtapp.modeler.primitives.object_names
        assert isinstance(self.aedtapp.modeler.get_vertices_of_line(my_name), list)
        rect = self.aedtapp.modeler.primitives.create_rectangle(
            self.aedtapp.PLANE.YZ, [0, -2, -2], [4, 3], name="rect_1"
        )
        swept = self.aedtapp.modeler.sweep_along_path(rect, path)
        assert swept
        assert rect.name in self.aedtapp.modeler.primitives.solid_names

    @pyaedt_unittest_check_desktop_error
    def test_22_sweep_along_vector(self):
        rect2 = self.aedtapp.modeler.primitives.create_rectangle(
            self.aedtapp.PLANE.YZ, [0, -2, -2], [4, 3], name="rect_2"
        )
        assert self.aedtapp.modeler.sweep_along_vector(rect2, [10, 20, 20])
        assert rect2.name in self.aedtapp.modeler.primitives.solid_names

    @pyaedt_unittest_check_desktop_error
    def test_23_create_rectangle(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.PLANE.XY
        o = self.aedtapp.modeler.primitives.create_rectangle(plane, udp, [4, 5], name="MyRectangle", matname="Copper")
        assert o.id > 0
        assert o.name.startswith("MyRectangle")
        assert o.object_type == "Sheet"
        assert o.is3d is False

    @pyaedt_unittest_check_desktop_error
    def test_24_create_cone(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        axis = self.aedtapp.AXIS.Z
        o = self.aedtapp.modeler.primitives.create_cone(axis, udp, 20, 10, 5, name="MyCone", matname="Copper")
        assert o.id > 0
        assert o.name.startswith("MyCone")
        assert o.object_type == "Solid"
        assert o.is3d is True

    @pyaedt_unittest_check_desktop_error
    def test_25_get_object_id(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.PLANE.XY
        o = self.aedtapp.modeler.primitives.create_rectangle(plane, udp, [4, 5], name="MyRectangle5")
        assert self.aedtapp.modeler.primitives.get_obj_id(o.name) == o.id

    @pyaedt_unittest_check_desktop_error
    def test_26_get_object_names(self):

        p1, p2, points = self.create_polylines()
        c1 = self.create_copper_box()
        r1 = self.create_rectangle()
        solid_list = self.aedtapp.modeler.primitives.solid_names
        sheet_list = self.aedtapp.modeler.primitives.sheet_names
        line_list = self.aedtapp.modeler.primitives.line_names
        all_objects_list = self.aedtapp.modeler.primitives.object_names

        assert c1.name in solid_list
        assert r1.name in sheet_list
        assert p1.name in line_list
        assert p2.name in line_list
        assert c1.name in all_objects_list
        assert r1.name in all_objects_list
        assert p1.name in all_objects_list
        assert p2.name in all_objects_list

        print("Solids")
        for solid in solid_list:
            solid_object = self.aedtapp.modeler.primitives[solid]

            print(solid)
            print(solid_object.name)

            assert solid_object.is3d
            assert solid_object.object_type == "Solid"

        print("Sheets")
        for sheet in sheet_list:
            sheet_object = self.aedtapp.modeler.primitives[sheet]
            print(sheet)
            print(sheet_object.name)
            assert self.aedtapp.modeler.primitives[sheet].is3d is False
            assert self.aedtapp.modeler.primitives[sheet].object_type == "Sheet"

        print("Lines")
        for line in line_list:
            line_object = self.aedtapp.modeler.primitives[line]
            print(line)
            print(line_object.name)
            assert self.aedtapp.modeler.primitives[line].is3d is False
            assert self.aedtapp.modeler.primitives[line].object_type == "Line"

        assert len(all_objects_list) == len(solid_list) + len(line_list) + len(sheet_list)

    @pyaedt_unittest_check_desktop_error
    def test_27_get_object_by_material(self):
        self.create_polylines()
        self.create_copper_box()
        self.create_rectangle()
        listsobj = self.aedtapp.modeler.primitives.get_objects_by_material("vacuum")
        assert len(listsobj) > 0
        listsobj = self.aedtapp.modeler.primitives.get_objects_by_material("FR4")
        assert len(listsobj) == 0

    @pyaedt_unittest_check_desktop_error
    def test_28_get_object_faces(self):
        self.create_rectangle()
        o = self.aedtapp.modeler.primitives["MyRectangle"]
        assert len(o.faces) == 1
        assert len(o.edges) == 4
        assert len(o.vertices) == 4

    def test_29_get_edges_from_position(self):
        self.cache.ignore_error_message_local("Script macro error: Can't find face by name and position.")
        o = self.create_rectangle(name="MyRectangle_for_primitives")
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        edge_id = self.aedtapp.modeler.primitives.get_edgeid_from_position(udp, o.name)
        assert edge_id > 0
        edge_id = self.aedtapp.modeler.primitives.get_edgeid_from_position(udp)
        assert edge_id > 0

    @pyaedt_unittest_check_desktop_error
    def test_30_get_faces_from_position(self):
        self.cache.ignore_error_message_local("Script macro error: Can't find face by name and position.")
        o = self.create_rectangle("New_Rectangle1")
        edge_id = self.aedtapp.modeler.primitives.get_faceid_from_position([5, 3, 8], "New_Rectangle1")
        assert edge_id > 0
        udp = self.aedtapp.modeler.Position(100, 100, 100)
        edge_id = self.aedtapp.modeler.primitives.get_faceid_from_position(udp)
        assert not edge_id

    @pyaedt_unittest_check_desktop_error
    def test_31_delete_object(self):
        self.create_rectangle(name="MyRectangle")
        assert "MyRectangle" in self.aedtapp.modeler.primitives.object_names
        deleted = self.aedtapp.modeler.primitives.delete("MyRectangle")
        assert deleted
        assert "MyRectangle" not in self.aedtapp.modeler.primitives.object_names

    @pyaedt_unittest_check_desktop_error
    def test_32_get_face_vertices(self):
        plane = self.aedtapp.PLANE.XY
        rectid = self.aedtapp.modeler.primitives.create_rectangle(plane, [1, 2, 3], [7, 13], name="rect_for_get")
        listfaces = self.aedtapp.modeler.primitives.get_object_faces("rect_for_get")
        vertices = self.aedtapp.modeler.primitives.get_face_vertices(listfaces[0])
        assert len(vertices) == 4

    @pyaedt_unittest_check_desktop_error
    def test_33_get_edge_vertices(self):
        listedges = self.aedtapp.modeler.primitives.get_object_edges("rect_for_get")
        vertices = self.aedtapp.modeler.primitives.get_edge_vertices(listedges[0])
        assert len(vertices) == 2

    @pyaedt_unittest_check_desktop_error
    def test_34_get_vertex_position(self):
        listedges = self.aedtapp.modeler.primitives.get_object_edges("rect_for_get")
        vertices = self.aedtapp.modeler.primitives.get_edge_vertices(listedges[0])
        pos1 = self.aedtapp.modeler.primitives.get_vertex_position(vertices[0])
        assert len(pos1) == 3
        pos2 = self.aedtapp.modeler.primitives.get_vertex_position(vertices[1])
        assert len(pos2) == 3
        edge_length = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2) ** 0.5
        assert edge_length == 7

    @pyaedt_unittest_check_desktop_error
    def test_35_get_face_area(self):
        listfaces = self.aedtapp.modeler.primitives.get_object_faces("rect_for_get")
        area = self.aedtapp.modeler.primitives.get_face_area(listfaces[0])
        assert area == 7 * 13

    @pyaedt_unittest_check_desktop_error
    def test_36_get_face_center(self):
        listfaces = self.aedtapp.modeler.primitives.get_object_faces("rect_for_get")
        center = self.aedtapp.modeler.primitives.get_face_center(listfaces[0])
        assert center == [4.5, 8.5, 3.0]

    @pyaedt_unittest_check_desktop_error
    def test_37_get_edge_midpoint(self):
        listedges = self.aedtapp.modeler.primitives.get_object_edges("rect_for_get")
        point = self.aedtapp.modeler.primitives.get_edge_midpoint(listedges[0])
        assert point == [4.5, 2.0, 3.0]

    @pyaedt_unittest_check_desktop_error
    def test_38_get_bodynames_from_position(self):
        center = [20, 20, 0]
        radius = 1
        id = self.aedtapp.modeler.primitives.create_sphere(center, radius, "fred")
        spherename = self.aedtapp.modeler.primitives.get_bodynames_from_position(center)
        assert "fred" in spherename

        plane = self.aedtapp.PLANE.XY
        rectid = self.aedtapp.modeler.primitives.create_rectangle(plane, [-50, -50, -50], [2, 2], name="bob")
        rectname = self.aedtapp.modeler.primitives.get_bodynames_from_position([-49.0, -49.0, -50.0])
        assert "bob" in rectname

        udp1 = self.aedtapp.modeler.Position(-23, -23, 13)
        udp2 = self.aedtapp.modeler.Position(-27, -27, 11)
        udp3 = self.aedtapp.modeler.Position(-31, -31, 7)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3, udp4]
        P = self.aedtapp.modeler.primitives.create_polyline(arrofpos, cover_surface=False, name="bill")
        polyname = self.aedtapp.modeler.primitives.get_bodynames_from_position([-27, -27, 11])
        assert "bill" in polyname

    @pyaedt_unittest_check_desktop_error
    def test_39_getobjects_with_strings(self):
        list1 = self.aedtapp.modeler.primitives.get_objects_w_string("MyCone")
        list2 = self.aedtapp.modeler.primitives.get_objects_w_string("my", False)

        assert len(list1) > 0
        assert len(list2) > 0

    @pyaedt_unittest_check_desktop_error
    def test_40_getmodel_objects(self):
        list1 = self.aedtapp.modeler.primitives.model_objects
        list2 = self.aedtapp.modeler.primitives.non_model_objects
        list3 = self.aedtapp.modeler.primitives.object_names
        for el in list1:
            if el not in list3:
                print("Missing {}".format(el))
        assert len(list1) + len(list2) == len(list3)

    @pyaedt_unittest_check_desktop_error
    def test_41a_create_rect_sheet_to_region(self):
        self.aedtapp.modeler.primitives.create_region()
        self.create_copper_box(name="MyBox_to_gnd")
        groundplane = self.aedtapp.modeler.create_sheet_to_ground("MyBox_to_gnd")
        assert groundplane.id > 0

    @pyaedt_unittest_check_desktop_error
    def test_41b_create_rect_sheet_to_groundplane(self):
        rect = self.create_rectangle()
        box = self.create_copper_box()
        plane = self.aedtapp.modeler.create_sheet_to_ground(box.name, rect.name, self.aedtapp.AxisDir.ZNeg)
        assert isinstance(plane, Object3d)

    @pyaedt_unittest_check_desktop_error
    def test_41b_get_edges_for_circuit_port(self):
        udp = self.aedtapp.modeler.Position(0, 0, 8)
        plane = self.aedtapp.PLANE.XY
        o = self.aedtapp.modeler.primitives.create_rectangle(plane, udp, [3, 10], name="MyGND", matname="Copper")
        face_id = o.faces[0].id
        edges1 = self.aedtapp.modeler.primitives.get_edges_for_circuit_port(
            face_id, XY_plane=True, YZ_plane=False, XZ_plane=False, allow_perpendicular=True, tol=1e-6
        )
        edges2 = self.aedtapp.modeler.primitives.get_edges_for_circuit_port_from_sheet(
            "MyGND", XY_plane=True, YZ_plane=False, XZ_plane=False, allow_perpendicular=True, tol=1e-6
        )

    @pyaedt_unittest_check_desktop_error
    def test_42_chamfer(self):
        self.cache.ignore_error_message_local("Wrong Type Entered. Type must be integer from 0 to 3")
        o = self.create_copper_box(name="MyBox")
        assert o.edges[0].chamfer()
        self.aedtapp._odesign.Undo()
        assert o.edges[0].chamfer(chamfer_type=1)
        self.aedtapp._odesign.Undo()
        assert o.edges[0].chamfer(chamfer_type=2)
        self.aedtapp._odesign.Undo()
        assert o.edges[0].chamfer(chamfer_type=3)
        self.aedtapp._odesign.Undo()
        assert not o.edges[0].chamfer(chamfer_type=4)

    @pyaedt_unittest_check_desktop_error
    def test_43_fillet_and_undo(self):
        o = self.create_copper_box(name="MyBox")
        assert o.edges[0].fillet()
        self.aedtapp._odesign.Undo()
        assert o.edges[0].fillet()

    @pyaedt_unittest_check_desktop_error
    def test_44_create_polyline_basic_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

        p1 = prim3D.create_polyline(position_list=test_points[0:2], name="PL01_line")
        assert len(p1.start_point) == 3
        assert len(p1.end_point) == 3
        assert prim3D.create_polyline(position_list=test_points[0:3], segment_type="Arc", name="PL02_arc")

        assert prim3D.create_polyline(
            position_list=test_points, segment_type=PolylineSegment("Spline", num_points=4), name="PL03_spline_4pt"
        )
        assert prim3D.create_polyline(
            position_list=test_points, segment_type=PolylineSegment("Spline", num_points=3), name="PL03_spline_3pt"
        )
        assert prim3D.create_polyline(position_list=test_points[0:3], segment_type="Spline", name="PL03_spline_str_3pt")
        assert prim3D.create_polyline(position_list=test_points[0:2], segment_type="Spline", name="PL03_spline_str_2pt")
        assert prim3D.create_polyline(
            position_list=[[100, 100, 0]],
            segment_type=PolylineSegment("AngularArc", arc_center=[0, 0, 0], arc_angle="30deg"),
            name="PL04_center_point_arc",
        )
        assert prim3D.create_polyline(
            position_list=[[100, 100, 0]],
            segment_type=PolylineSegment("AngularArc", arc_angle="30deg"),
            name="PL04_center_point_arc",
        )

    @pyaedt_unittest_check_desktop_error
    def test_45_create_circle_from_2_arc_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        assert prim3D.create_polyline(
            position_list=[[34.1004, 14.1248, 0], [27.646, 16.7984, 0], [24.9725, 10.3439, 0], [31.4269, 7.6704, 0]],
            segment_type=["Arc", "Arc"],
            cover_surface=True,
            close_surface=True,
            name="Rotor_Subtract_25_0",
            matname="vacuum",
        )

    @pyaedt_unittest_check_desktop_error
    def test_46_compound_polylines_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

        assert prim3D.create_polyline(position_list=test_points, name="PL06_segmented_compound_line")
        assert prim3D.create_polyline(
            position_list=test_points, segment_type=["Line", "Arc"], name="PL05_compound_line_arc"
        )
        assert prim3D.create_polyline(
            position_list=test_points, close_surface=True, name="PL07_segmented_compound_line_closed"
        )
        assert prim3D.create_polyline(
            position_list=test_points, cover_surface=True, name="SPL01_segmented_compound_line"
        )

    @pyaedt_unittest_check_desktop_error
    def test_47_insert_polylines_segments_test1(self):
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]
        P = self.aedtapp.modeler.primitives.create_polyline(
            position_list=test_points, close_surface=True, name="PL08_segmented_compound_insert_segment"
        )
        assert P
        start_point = P.start_point
        insert_point = ["90mm", "20mm", "0mm"]
        insert_point2 = ["95mm", "20mm", "0mm"]
        assert P.insert_segment(position_list=[start_point, insert_point])
        assert P.insert_segment(position_list=[insert_point, insert_point2])

    @pyaedt_unittest_check_desktop_error
    def test_48_insert_polylines_segments_test2(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm", "p1", "0mm"], ["-p1", "0mm", "0mm"], ["-p1/2", "-p1/2", "0mm"], ["0mm", "0mm", "0mm"]]

        P = prim3D.create_polyline(
            position_list=test_points, close_surface=False, name="PL08_segmented_compound_insert_arc"
        )
        start_point = P.vertex_positions[1]
        insert_point1 = ["90mm", "20mm", "0mm"]
        insert_point2 = [40, 40, 0]

        P.insert_segment(position_list=[start_point, insert_point1, insert_point2], segment="Arc")

    @pyaedt_unittest_check_desktop_error
    def test_49_modify_crossection(self):

        P = self.aedtapp.modeler.primitives.create_polyline(
            position_list=[[34.1004, 14.1248, 0], [27.646, 16.7984, 0], [24.9725, 10.3439, 0]],
            name="Rotor_Subtract_25_0",
            matname="copper",
        )
        P1 = P.clone()
        P2 = P.clone()
        P3 = P.clone()
        P4 = P.clone()

        P1.set_crosssection_properties(type="Line", width="1mm")
        a = P1.object_type

        P2.set_crosssection_properties(type="Circle", width="1mm", num_seg=5)
        P3.set_crosssection_properties(type="Rectangle", width="1mm", height="1mm")
        P4.set_crosssection_properties(type="Isosceles Trapezoid", width="1mm", height="1mm", topwidth="4mm")

        assert P.object_type == "Line"
        assert P1.object_type == "Sheet"
        assert P2.object_type == "Solid"
        assert P3.object_type == "Solid"
        assert P4.object_type == "Solid"

    @pyaedt_unittest_check_desktop_error
    def test_50_remove_vertex_from_polyline(self):

        p1, p2, test_points = self.create_polylines("Poly_remove_")

        P = self.aedtapp.modeler.primitives["Poly_remove_segmented"]
        P.remove_vertex(test_points[2])
        time.sleep(0.1)
        P1 = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P1.remove_vertex([0, 1, 2])
        time.sleep(0.1)

        P2 = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2.remove_vertex(["0mm", "1mm", "2mm"])
        time.sleep(0.1)

        P3 = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P3.remove_vertex(["0mm", "1mm", "2mm"], abstol=1e-6)

    @pyaedt_unittest_check_desktop_error
    def test_51_remove_edges_from_polyline(self):

        primitives = self.aedtapp.modeler.primitives
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_edges(edge_id=0)
        assert P.name in self.aedtapp.modeler.primitives.line_names
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_edges(edge_id=[0, 1])
        assert P.name in self.aedtapp.modeler.primitives.line_names
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_edges(edge_id=[1, 2])
        assert P.name in self.aedtapp.modeler.primitives.line_names
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4], [3, 1, 6]])
        P.remove_edges(edge_id=2)
        assert P.name in self.aedtapp.modeler.primitives.line_names

    @pyaedt_unittest_check_desktop_error
    def test_52_remove_edges_from_polyline_invalid(self):
        self.cache.ignore_error_message_local("Body could not be created for part ")
        P = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_edges(edge_id=[0, 1])
        assert not P.name in self.aedtapp.modeler.primitives.line_names

    @pyaedt_unittest_check_desktop_error
    def test_53_duplicate_polyline_and_manipulate(self):
        # TODO Figure this one out !
        self.cache.ignore_error_message_local("Body could not be created for part NewObject_")
        P1 = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2 = P1.clone()
        assert P2.id != P1.id

    @pyaedt_unittest_check_desktop_error
    def test_54_create_bond_wires(self):
        self.cache.ignore_error_message_local("Wrong Profile Type")
        b1 = self.aedtapp.modeler.primitives.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, facets=8, matname="copper", name="jedec51"
        )
        assert b1
        b2 = self.aedtapp.modeler.primitives.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, bond_type=1, matname="copper", name="jedec41"
        )
        assert b2
        b2 = self.aedtapp.modeler.primitives.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, bond_type=2, matname="copper", name="jedec41"
        )
        assert b2
        b2 = self.aedtapp.modeler.primitives.create_bondwire(
            [0, 0, 0], [10, 10, 2], h1=0.15, h2=0, diameter=0.034, bond_type=3, matname="copper", name="jedec41"
        )
        assert not b2

    @pyaedt_unittest_check_desktop_error
    def test_56_create_group(self):
        assert self.aedtapp.modeler.create_group(["jedec51", "jedec41"], "mygroup")
        assert self.aedtapp.modeler.ungroup("mygroup")

    @pyaedt_unittest_check_desktop_error
    def test_57_flatten_assembly(self):
        assert self.aedtapp.modeler.flatten_assembly()

    @pyaedt_unittest_check_desktop_error
    def test_58_solving_volume(self):
        vol = self.aedtapp.modeler.get_solving_volume()
        assert float(vol) > 0

    @pyaedt_unittest_check_desktop_error
    def test_59_lines(self):
        assert self.aedtapp.modeler.vertex_data_of_lines()

    @pytest.mark.skipif("UNITTEST_CURRENT_TEST" in os.environ, reason="Issue in IronPython")
    @pyaedt_unittest_check_desktop_error
    def test_60_get_edges_on_bounding_box(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.aedtapp.load_project(self.test_99_project)
        edges = self.aedtapp.modeler.primitives.get_edges_on_bounding_box(
            ["Port1", "Port2"], return_colinear=True, tol=1e-6
        )
        assert len(edges) == 2
        edges = self.aedtapp.modeler.primitives.get_edges_on_bounding_box(
            ["Port1", "Port2"], return_colinear=False, tol=1e-6
        )
        assert len(edges) == 4

    @pyaedt_unittest_check_desktop_error
    def test_61_get_closest_edge_to_position(self):
        my_box = self.create_copper_box("test_closest_edge")
        assert isinstance(self.aedtapp.modeler.primitives.get_closest_edgeid_to_position([0.2, 0, 0]), int)
        pass

    @pytest.mark.skipif(config["build_machine"] or is_ironpython, reason="Not running in non-graphical mode")
    @pyaedt_unittest_check_desktop_error
    def test_62_import_space_claim(self):
        self.aedtapp.insert_design("SCImport")
        assert self.aedtapp.modeler.import_spaceclaim_document(os.path.join(self.local_scratch.path, scdoc))
        assert len(self.aedtapp.modeler.primitives.objects) == 1

    def test_63_import_step(self):
        self.aedtapp.insert_design("StepImport")
        assert self.aedtapp.modeler.import_3d_cad(self.step_file)
        assert len(self.aedtapp.modeler.primitives.object_names) == 1

    @pyaedt_unittest_check_desktop_error
    def test_64_create_equationbased_curve(self):
        self.aedtapp.insert_design("Equations")
        eq_line = self.aedtapp.modeler.primitives.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=0)
        assert len(eq_line.edges) == 1
        eq_segmented = self.aedtapp.modeler.primitives.create_equationbased_curve(x_t="_t", y_t="_t*2", num_points=5)
        assert len(eq_segmented.edges) == 4

        eq_xsection = self.aedtapp.modeler.primitives.create_equationbased_curve(
            x_t="_t", y_t="_t*2", xsection_type="Circle"
        )
        assert eq_xsection.name in self.aedtapp.modeler.primitives.solid_names

    def test_65_create_3dcomponent(self):
        self.aedtapp["l_dipole"] = "13.5cm"

        compfile = self.aedtapp.components3d["Dipole_Antenna_DM"]
        geometryparams = self.aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        geometryparams["dipole_length"] = "l_dipole"
        name = self.aedtapp.modeler.primitives.insert_3d_component(compfile, geometryparams)
        assert isinstance(name, str)

    def test_65b_group_components(self):
        self.aedtapp["l_dipole"] = "13.5cm"

        compfile = self.aedtapp.components3d["Dipole_Antenna_DM"]
        geometryparams = self.aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        geometryparams["dipole_length"] = "l_dipole"
        name = self.aedtapp.modeler.primitives.insert_3d_component(compfile, geometryparams)
        name2 = self.aedtapp.modeler.primitives.insert_3d_component(compfile, geometryparams)
        assert self.aedtapp.modeler.create_group(components=[name, name2], group_name="test_group") == "test_group"

    @pyaedt_unittest_check_desktop_error
    def test_66_assign_material(self):
        box1 = self.aedtapp.modeler.primitives.create_box([60, 60, 60], [4, 5, 5])
        box2 = self.aedtapp.modeler.primitives.create_box([50, 50, 50], [2, 3, 4])
        cyl1 = self.aedtapp.modeler.primitives.create_cylinder(cs_axis="X", position=[50, 0, 0], radius=1, height=20)
        cyl2 = self.aedtapp.modeler.primitives.create_cylinder(cs_axis="Z", position=[0, 0, 50], radius=1, height=10)

        objects_list = [box1, box2, cyl1, cyl2]
        self.aedtapp.assign_material(objects_list, "copper")
        assert self.aedtapp.modeler.primitives[box1].material_name == "copper"
        assert self.aedtapp.modeler.primitives[box2].material_name == "copper"
        assert self.aedtapp.modeler.primitives[cyl1].material_name == "copper"
        assert self.aedtapp.modeler.primitives[cyl2].material_name == "copper"

        obj_names_list = [box1.name, box2.name, cyl1.name, cyl2.name]
        self.aedtapp.assign_material(obj_names_list, "aluminum")
        assert self.aedtapp.modeler.primitives[box1].material_name == "aluminum"
        assert self.aedtapp.modeler.primitives[box2].material_name == "aluminum"
        assert self.aedtapp.modeler.primitives[cyl1].material_name == "aluminum"
        assert self.aedtapp.modeler.primitives[cyl2].material_name == "aluminum"

    @pyaedt_unittest_check_desktop_error
    def test_67_cover_lines(self):
        P1 = self.aedtapp.modeler.primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]], close_surface=True)
        assert self.aedtapp.modeler.cover_lines(P1)
