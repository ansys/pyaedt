# standard imports
import os
# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt.core import Hfss
from pyaedt.core.generic.filesystem import Scratch
import gc

class TestPrimitives:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            test_primitives_projectfile = os.path.join(self.local_scratch.path, 'test_primitives' + '.aedt')
            self.aedtapp = Hfss()
            self.aedtapp.save_project(project_file=test_primitives_projectfile)
            self.prim = self.aedtapp.modeler.primitives

            test_98_project = os.path.join(local_path, 'example_models', 'assembly2' + '.aedt')
            self.test_98_project = self.local_scratch.copyfile(test_98_project)
            test_99_project = os.path.join(local_path, 'example_models', 'assembly' + '.aedt')
            self.test_99_project = self.local_scratch.copyfile(test_99_project)

    def teardown_class(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_box(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        dimensions = [10, 10, 5]
        id = self.prim.create_box(udp, dimensions, "Mybox", "Copper")
        assert id > 0
        assert self.prim[id].name == "Mybox"
        assert self.prim[id].object_type == "Solid"
        assert self.prim[id].is3d == True

    def test_01_check_object_faces(self):
        assert len(self.prim["Mybox"].faces) == 6
        f = self.prim["Mybox"].faces[0]
        assert type(f.center) is list and len(f.center) == 3
        assert type(f.area) is float and f.area > 0
        assert self.prim["Mybox"].faces[0].move_with_offset(0.1)
        assert self.prim["Mybox"].faces[0].move_with_vector([0,0,0.01])
        assert type(f.normal) is list


    def test_01_check_object_edges(self):
        e = self.prim["Mybox"].edges[1]
        assert type(e.midpoint) is list and len(e.midpoint) == 3
        assert type(e.length) is float and e.length> 0

    def test_01_check_object_vertices(self):
        assert len(self.prim["Mybox"].vertices)==8
        v = self.prim["Mybox"].vertices[0]
        assert type(v.position) is list and len(v.position) == 3



    def test_02_create_circle(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_circle(plane, udp, 2, name="MyCircle", matname="Copper")
        assert id > 0
        assert self.prim[id].name == "MyCircle"
        assert self.prim[id].object_type == "Sheet"
        assert self.prim[id].is3d is False

    def test_04_create_sphere(self):
        udp = self.aedtapp.modeler.Position(20,20, 0)
        radius = 5
        id = self.prim.create_sphere(udp, radius, "MySphere", "Copper")
        assert id > 0
        assert self.prim[id].name == "MySphere"
        assert self.prim[id].object_type == "Solid"
        assert self.prim[id].is3d is True

    def test_05_create_cylinder(self):
        udp = self.aedtapp.modeler.Position(20,20, 0)
        axis = self.aedtapp.CoordinateSystemAxis.YAxis
        radius = 5
        height = 50
        id = self.prim.create_cylinder(axis, udp, radius, height, 8, "MyCyl", "Copper")
        assert id > 0
        assert self.prim[id].name == "MyCyl"
        assert self.prim[id].object_type == "Solid"
        assert self.prim[id].is3d is True
        pass

    def test_06_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_ellipse(plane, udp, 5,1.5,True, name="MyEllpise01", matname="Copper")
        assert id > 0
        assert self.prim[id].name == "MyEllpise01"
        assert self.prim[id].object_type == "Sheet"
        assert self.prim[id].is3d is False
        id = self.prim.create_ellipse(plane, udp, 5,1.5,False, name="MyEllpise02")
        assert id > 0
        assert self.prim[id].name == "MyEllpise02"
        assert self.prim[id].object_type == "Line"
        assert self.prim[id].is3d is False
        pass

    def test_07_create_object_from_edge(self):
        edges = self.prim.get_object_edges(self.prim.get_obj_id("MyCyl"))
        id = self.prim.create_object_from_edge(edges[0])
        assert id>0
        assert self.prim[id].object_type == "Line"
        assert self.prim[id].is3d is False
        pass

    def test_08_create_object_from_face(self):
        faces = self.prim.get_object_faces(self.prim.get_obj_id("MyCyl"))
        id = self.prim.create_object_from_face(faces[0])
        assert id>0
        assert self.prim[id].object_type == "Sheet"
        assert self.prim[id].is3d is False
        pass

    def test_09_create_polyline(self):
        udp1 = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(5, 0, 0)
        udp3 = self.aedtapp.modeler.Position(5, 5, 0)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp4, udp2, udp3, udp1]
        id6 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, coversurface=True, name="Poly1", matname="Copper")
        assert type(id6) is int
        assert self.prim[id6].object_type == "Sheet"
        assert self.prim[id6].is3d is False

    def test_10_create_polyline_with_crosssection(self):
        udp1 = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(5, 0, 0)
        udp3 = self.aedtapp.modeler.Position(5, 5, 0)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3]
        id5 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly2")
        self.aedtapp.modeler.primitives.create_polyline_with_crosssection("Poly2")
        assert type(id5) is int
        assert self.prim[id5].object_type == "Solid"
        assert self.prim[id5].is3d is True

    def test_11_create_rectangle(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_rectangle(plane, udp, [4, 5], name="MyRectangle", matname="Copper")
        assert id > 0
        assert self.prim[id].name == "MyRectangle"
        assert self.prim[id].object_type == "Sheet"
        assert self.prim[id].is3d is False

    def test_12_create_cone(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        axis = self.aedtapp.CoordinateSystemAxis.ZAxis
        id = self.prim.create_cone(axis, udp, 20, 10 ,5 , name="MyCone", matname="Copper")
        assert id > 0
        assert self.prim[id].name == "MyCone"
        assert self.prim[id].object_type == "Solid"
        assert self.prim[id].is3d is True

    def test_13_get_object_name(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        axis = self.aedtapp.CoordinateSystemAxis.ZAxis
        id = self.prim.create_cone(axis, udp, 20, 10, 5, name="MyCone2")
        assert self.prim.get_obj_name(id) == "MyCone2"

    def test_13_get_object_id(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_rectangle(plane, udp, [4, 5], name="MyRectangle5")
        assert self.prim.get_obj_id("MyRectangle5") is id

    def test_14_get_object_names(self):
        objnames = self.prim.get_all_objects_names()
        solidnames = self.prim.get_all_objects_names(get_lines=False, get_sheets=False)
        for i in solidnames:
            assert self.prim.objects[self.prim.get_obj_id(i)].is3d
            assert self.prim.objects[self.prim.get_obj_id(i)].object_type is "Solid"
        sheetnames = self.prim.get_all_objects_names(get_lines=False, get_solids=False)
        for i in sheetnames:
            assert self.prim.objects[self.prim.get_obj_id(i)].is3d is False
            assert self.prim.objects[self.prim.get_obj_id(i)].object_type is "Sheet"
        listnames = self.prim.get_all_objects_names(get_sheets=False, get_solids=False)
        for i in listnames:
            assert self.prim.objects[self.prim.get_obj_id(i)].is3d is False
            assert self.prim.objects[self.prim.get_obj_id(i)].object_type is "Line"
        assert len(objnames) == len(solidnames)+len(listnames)+len(sheetnames)

    def test_15_get_object_by_material(self):
        listsobj = self.prim.get_objects_by_material("vacuum")
        assert len(listsobj) > 0
        listsobj = self.prim.get_objects_by_material("FR4")
        assert len(listsobj) == 0

    def test_16_get_object_faces(self):
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_rectangle(plane, udp, [4, 5], name="MyRectangl_new")
        listsobj = self.prim.get_object_faces("MyRectangl_new")
        assert len(listsobj) == 1

    def test_17_get_object_edges(self):
        listsobj = self.prim.get_object_edges("MyRectangl_new")
        assert len(listsobj) == 4

    def test_18_get_object_vertex(self):
        listsobj = self.prim.get_object_vertices("MyRectangl_new")
        assert len(listsobj) == 4

    def test_19_get_edges_from_position(self):
        self.aedtapp.odesktop.CloseAllWindows()
        self.aedtapp.oproject.SetActiveDesign(self.aedtapp.odesign.GetName())
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        edge_id = self.prim.get_edgeid_from_position(udp, "MyRectangl_new")
        assert edge_id > 0
        edge_id = self.prim.get_edgeid_from_position(udp)
        assert edge_id > 0

    def test_20_get_faces_from_position(self):
        self.aedtapp.odesktop.CloseAllWindows()
        self.aedtapp.oproject.SetActiveDesign(self.aedtapp.odesign.GetName())
        udp = self.aedtapp.modeler.Position(5, 3, 8)
        edge_id = self.prim.get_faceid_from_position(udp, "MyRectangl_new")
        assert edge_id>0
        udp = self.aedtapp.modeler.Position(100, 100, 100)
        edge_id = self.prim.get_faceid_from_position(udp)
        assert edge_id==-1

    def test_21_delete_object(self):
        deleted = self.aedtapp.modeler.primitives.delete("MyRectangl_new")
        assert deleted
        assert "MyRectangl_new" not in self.prim.get_all_objects_names()

    def test_22_get_face_vertices(self):
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        rectid = self.prim.create_rectangle(plane, [1, 2, 3], [7, 13], name="rect_for_get")
        listfaces = self.prim.get_object_faces("rect_for_get")
        vertices = self.prim.get_face_vertices(listfaces[0])
        assert len(vertices) == 4

    def test_23_get_edge_vertices(self):
        listedges = self.prim.get_object_edges("rect_for_get")
        vertices = self.prim.get_edge_vertices(listedges[0])
        assert len(vertices) == 2

    def test_24_get_vertex_position(self):
        listedges = self.prim.get_object_edges("rect_for_get")
        vertices = self.prim.get_edge_vertices(listedges[0])
        pos1 = self.prim.get_vertex_position(vertices[0])
        assert len(pos1) == 3
        pos2 = self.prim.get_vertex_position(vertices[1])
        assert len(pos2) == 3
        edge_length = ( (pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2 )**0.5
        assert edge_length == 7

    def test_25_get_face_area(self):
        listfaces = self.prim.get_object_faces("rect_for_get")
        area = self.prim.get_face_area(listfaces[0])
        assert area == 7*13

    def test_26_get_face_center(self):
        listfaces = self.prim.get_object_faces("rect_for_get")
        center = self.prim.get_face_center(listfaces[0])
        assert center == [4.5, 8.5, 3.0]

    def test_27_get_edge_midpoint(self):
        listedges = self.prim.get_object_edges("rect_for_get")
        point = self.prim.get_edge_midpoint(listedges[0])
        assert point == [4.5, 2.0, 3.0]

    def test_28_get_bodynames_from_position(self):
        center = [20, 20, 0]
        radius = 1
        id = self.prim.create_sphere(center, radius, "fred")
        spherename = self.prim.get_bodynames_from_position(center)
        assert "fred" in spherename

        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        rectid = self.prim.create_rectangle(plane, [-50, -50, -50], [2, 2], name="bob")
        rectname = self.prim.get_bodynames_from_position([-49.0, -49.0, -50.0])
        assert "bob" in rectname

        udp1 = self.aedtapp.modeler.Position(-23, -23, 13)
        udp2 = self.aedtapp.modeler.Position(-27, -27, 11)
        udp3 = self.aedtapp.modeler.Position(-31, -31, 7)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3, udp4]
        id6 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, coversurface=False, name="bill")
        polyname = self.prim.get_bodynames_from_position([-27, -27, 11])
        assert "bill" in polyname

    def test_29_getobjects_with_strings(self):
        list1 = self.aedtapp.modeler.primitives.get_objects_w_string("MyCone")
        list2 = self.aedtapp.modeler.primitives.get_objects_w_string("my", False)

        assert len(list1) > 0
        assert len(list2) > 0

    def test_30_getmodel_objects(self):
        list1 = self.aedtapp.modeler.primitives.get_model_objects()
        list2 = self.aedtapp.modeler.primitives.get_model_objects(False)
        list3 = self.aedtapp.modeler.primitives.get_all_objects_names()
        assert len(list1) + len(list2) == len(list3)

    def test_31_create_rect_sheet_to_ground(self):
        assert self.aedtapp.modeler.create_sheet_to_ground("Mybox")>0
        assert self.aedtapp.modeler.create_sheet_to_ground("Mybox", "MyRectangle",self.aedtapp.AxisDir.ZNeg)>0

    # def test_98_get_edges_for_circuit_port(self):
    #     self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
    #     self.aedtapp.load_project(self.test_98_project)
    #     self.prim.refresh_all_ids()
    #     edges1 = self.prim.get_edges_for_circuit_port('Port1', XY_plane=False, YZ_plane=True, XZ_plane=False,
    #                                                   allow_perpendicular=False, tol=1e-6)
    #     assert edges1 == [5519, 5249]
    #     edges2 = self.prim.get_edges_for_circuit_port('Port2', XY_plane=False, YZ_plane=True, XZ_plane=False,
    #                                                   allow_perpendicular=False, tol=1e-6)
    #     assert edges2 == [5530, 5477]

    def test_32_chamfer(self):

        assert self.aedtapp.modeler.chamfer("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0])
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.chamfer("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0], chamfer_type=1)
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.chamfer("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0], chamfer_type=2)
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.chamfer("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0], chamfer_type=3)
        self.aedtapp.odesign.Undo()
        assert not self.aedtapp.modeler.chamfer("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0], chamfer_type=4)
        assert self.aedtapp.modeler.primitives["Mybox"].edges[0].chamfer()
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.primitives["Mybox"].edges[0].chamfer(chamfer_type=1)
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.primitives["Mybox"].edges[0].chamfer(chamfer_type=2)
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.primitives["Mybox"].edges[0].chamfer(chamfer_type=3)
        self.aedtapp.odesign.Undo()
        assert not self.aedtapp.modeler.primitives["Mybox"].edges[0].chamfer(chamfer_type=5)

    def test_33_fillet(self):

        assert self.aedtapp.modeler.fillet("Mybox", self.aedtapp.modeler.primitives["Mybox"].edges[0])
        self.aedtapp.odesign.Undo()
        assert self.aedtapp.modeler.primitives["Mybox"].edges[0].fillet()
        self.aedtapp.odesign.Undo()


    def test_99_get_edges_on_bunding_box(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.aedtapp.load_project(self.test_99_project)
        self.prim.refresh_all_ids()
        edges = self.prim.get_edges_on_bunding_box(['Port1', 'Port2'], return_colinear=True, tol=1e-6)
        assert edges == [5219, 5183]
        edges = self.prim.get_edges_on_bunding_box(['Port1', 'Port2'], return_colinear=False, tol=1e-6)
        assert edges == [5237, 5255, 5273, 5291]

