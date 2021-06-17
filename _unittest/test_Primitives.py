# standard imports
import os
# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
from pyaedt.modeler.Primitives import Polyline, PolylineSegment
import gc
import pytest
from .conftest import config
scdoc = "input.scdoc"
step = "input.stp"



class TestPrimitives:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            test_primitives_projectfile = os.path.join(self.local_scratch.path, 'test_primitives' + '.aedt')
            self.aedtapp = Hfss()
            self.aedtapp.save_project(project_file=test_primitives_projectfile)
            self.prim = self.aedtapp.modeler.primitives
            scdoc_file = os.path.join(local_path, 'example_models', scdoc)
            self.local_scratch.copyfile(scdoc_file)
            step_file = os.path.join(local_path, 'example_models', step)
            self.local_scratch.copyfile(step_file)
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
        id2 = self.prim.create_box(udp, dimensions)
        assert id > 0
        assert self.prim[id].name == "Mybox"
        assert self.prim[id].object_type == "Solid"
        assert self.prim[id].is3d == True

        id2 = self.prim.create_box(udp, dimensions)
        assert len(self.prim[id2].name) == 16
        assert self.prim[id2]._material_name == "vacuum"


    def test_01a_get_faces_from_mat(self):
        if not self.prim["Mybox"]:
            self.test_01_create_box()
        faces = self.aedtapp.modeler.select_allfaces_from_mat("Copper")
        assert len(faces)==6

    def test_01b_check_object_faces(self):

        if not self.prim["Mybox"]:
            self.test_01_create_box()

        face_list = self.prim["Mybox"].faces
        assert len(face_list) == 6
        f = self.prim["Mybox"].faces[0]
        assert type(f.center) is list and len(f.center) == 3
        assert type(f.area) is float and f.area > 0
        assert self.prim["Mybox"].faces[0].move_with_offset(0.1)
        assert self.prim["Mybox"].faces[0].move_with_vector([0,0,0.01])
        assert type(f.normal) is list

    def test_01c_check_object_edges(self):
        e = self.prim["Mybox"].edges[1]
        assert type(e.midpoint) is list and len(e.midpoint) == 3
        assert type(e.length) is float and e.length> 0

    def test_01d_check_object_vertices(self):
        assert len(self.prim["Mybox"].vertices)==8
        v = self.prim["Mybox"].vertices[0]
        assert type(v.position) is list and len(v.position) == 3

    def test_02_get_objects_in_group(self):
        objs = self.aedtapp.modeler.get_objects_in_group("Solids")
        assert type(objs) is list

    def test_03_create_circle(self):
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
        P1 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, cover_surface=True, name="Poly1", matname="Copper")
        P2 = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly2", matname="Copper")
        assert isinstance(P1, Polyline)
        assert isinstance(P2, Polyline)
        assert self.prim[P1.id].object_type == "Sheet"
        assert self.prim[P1.id].is3d is False
        assert self.prim[P2.id].object_type == "Line"
        assert self.prim[P2.id].is3d is False

    def test_10_create_polyline_with_crosssection(self):
        udp1 = self.aedtapp.modeler.Position(0, 0, 0)
        udp2 = self.aedtapp.modeler.Position(5, 0, 0)
        udp3 = self.aedtapp.modeler.Position(5, 5, 0)
        udp4 = self.aedtapp.modeler.Position(2, 5, 3)
        arrofpos = [udp1, udp2, udp3]
        P = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="Poly2", xsection_type="Rectangle")
        assert isinstance(P, Polyline)
        assert self.prim[P.id].object_type == "Solid"
        assert self.prim[P.id].is3d is True

    def test_10_sweep_along_path(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        udp3 = [5, 5, 0]
        arrofpos = [udp1, udp2, udp3]
        P = self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector")
        assert type(self.aedtapp.modeler.get_vertices_of_line("poly_vector")) is list
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.YZPlane, [0,-2,-2],[4,3], name="rect_1")
        assert self.aedtapp.modeler.sweep_along_path(rect, P.id )


    def test_10_sweep_around_axis(self):
        udp1 = [0, 0, 0]
        udp2 = [5, 0, 0]
        arrofpos = [udp1, udp2]
        self.aedtapp.modeler.primitives.create_polyline(arrofpos, name="poly_vector_2")
        assert self.aedtapp.modeler.sweep_around_axis("poly_vector_2", self.aedtapp.CoordinateSystemAxis.YAxis)

    def test_10_sweep_along_vector(self):
        rect2 = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.YZPlane, [0,-2,-2],[4,3], name="rect_2")
        assert self.aedtapp.modeler.sweep_along_vector(rect2, [10,20,20] )

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
        assert self.prim.get_obj_id("MyRectangle5") == id

    def test_14_get_object_names(self):
        if not self.prim["Mybox"]:
            self.test_01_create_box()
        if not self.prim["MyRectangle"]:
            self.test_11_create_rectangle()
        if not self.prim["Poly1"]:
            self.test_09_create_polyline()

        solid_list = self.prim.solids
        sheet_list = self.prim.sheets
        line_list = self.prim.lines
        all_objects_list = self.prim.object_names

        assert "Mybox" in solid_list
        assert "MyRectangle" in sheet_list
        assert "Poly1" in sheet_list
        assert "Poly2" in line_list
        assert "Mybox" in all_objects_list
        assert "MyRectangle" in all_objects_list
        assert "Poly1" in all_objects_list
        assert "Poly2" in all_objects_list

        objnames = self.prim.get_all_objects_names()
        solidnames = self.prim.get_all_objects_names(get_lines=False, get_sheets=False)
        for solid in solidnames:
            solid_object = self.prim[solid]
            assert solid_object.is3d
            assert solid_object.object_type is "Solid"
        sheetnames = self.prim.get_all_objects_names(get_lines=False, get_solids=False)
        for sheet in sheetnames:
            assert self.prim[sheet].is3d is False
            assert self.prim[sheet].object_type is "Sheet"
        listnames = self.prim.get_all_objects_names(get_sheets=False, get_solids=False)
        for line in listnames:
            assert self.prim[line].is3d is False
            assert self.prim[line].object_type is "Line"
        assert len(objnames) == len(solidnames) + len(listnames) + len(sheetnames)

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
        if not self.prim["rect_for_get"]:
            self.test_22_get_face_vertices()
        listfaces = self.prim.get_object_faces("rect_for_get")
        area = self.prim.get_face_area(listfaces[0])
        assert area == 7*13

    def test_26_get_face_center(self):
        if not self.prim["rect_for_get"]:
            self.test_22_get_face_vertices()
        listfaces = self.prim.get_object_faces("rect_for_get")
        center = self.prim.get_face_center(listfaces[0])
        assert center == [4.5, 8.5, 3.0]

    def test_27_get_edge_midpoint(self):
        if not self.prim["rect_for_get"]:
            self.test_22_get_face_vertices()
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
        P = self.aedtapp.modeler.primitives.create_polyline(arrofpos, cover_surface=False, name="bill")
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
        if not self.prim["Mybox"]:
            self.test_01_create_box()
        if not self.prim["MyRectangle"]:
            self.test_11_create_rectangle()

        id = self.aedtapp.modeler.create_sheet_to_ground("Mybox")
        assert id > 0
        assert self.aedtapp.modeler.create_sheet_to_ground("Mybox", "MyRectangle",self.aedtapp.AxisDir.ZNeg)>0

    def test_31b_get_edges_for_circuit_port(self):
        udp = self.aedtapp.modeler.Position(0, 0, 8)
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        id = self.prim.create_rectangle(plane, udp, [3, 10], name="MyGND", matname="Copper")
        face_id = self.aedtapp.modeler.primitives["MyRectangle"].faces[0].id
        edges1 = self.aedtapp.modeler.primitives.get_edges_for_circuit_port(face_id, XY_plane=True, YZ_plane=False, XZ_plane=False,
                                                      allow_perpendicular=True, tol=1e-6)
        edges2 = self.aedtapp.modeler.primitives.get_edges_for_circuit_port_from_sheet("MyRectangle", XY_plane=True, YZ_plane=False, XZ_plane=False,
                                                      allow_perpendicular=True, tol=1e-6)

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

    def test_34_create_polyline_basic_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm",     "p1",     "0mm"],
                       ["-p1",     "0mm",    "0mm"],
                       ["-p1/2",   "-p1/2",  "0mm"],
                       ["0mm",     "0mm",    "0mm"]]

        assert prim3D.create_polyline(position_list=test_points[0:2], name="PL01_line")
        assert prim3D.create_polyline(position_list=test_points[0:3], segment_type="Arc", name="PL02_arc")

        assert prim3D.create_polyline(position_list=test_points,
                                      segment_type=PolylineSegment("Spline", num_points=4),
                                      name="PL03_spline_4pt")
        assert prim3D.create_polyline(position_list=test_points,
                                      segment_type=PolylineSegment("Spline", num_points=3),
                                      name="PL03_spline_3pt")
        assert prim3D.create_polyline(position_list=test_points[0:3],
                                      segment_type="Spline",
                                      name="PL03_spline_str_3pt")
        assert prim3D.create_polyline(position_list=test_points[0:2],
                                      segment_type="Spline",
                                      name="PL03_spline_str_2pt")
        assert prim3D.create_polyline(position_list=[[100, 100, 0]],
                                      segment_type=PolylineSegment("AngularArc", arc_center=[0, 0, 0], arc_angle="30deg"),
                                      name="PL04_center_point_arc")

    def test_35_create_circle_from_2_arc_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        assert prim3D.create_polyline(position_list=[[34.1004, 14.1248, 0],
                                                     [27.646, 16.7984, 0],
                                                     [24.9725, 10.3439, 0],
                                                     [31.4269, 7.6704, 0]],
                                      segment_type=["Arc", "Arc"],
                                      cover_surface=True, close_surface=True,
                                      name="Rotor_Subtract_25_0", matname="vacuum")

    def test_36_compound_polylines_segments(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm",     "p1",     "0mm"],
                       ["-p1",     "0mm",    "0mm"],
                       ["-p1/2",   "-p1/2",  "0mm"],
                       ["0mm",     "0mm",    "0mm"]]

        assert prim3D.create_polyline(position_list=test_points, name="PL06_segmented_compound_line")
        assert prim3D.create_polyline(position_list=test_points, segment_type=["Line", "Arc"],
                                      name="PL05_compound_line_arc")
        assert prim3D.create_polyline(position_list=test_points,
                                      close_surface=True,
                                      name="PL07_segmented_compound_line_closed")
        assert prim3D.create_polyline(position_list=test_points,
                                      cover_surface=True,
                                      name="SPL01_segmented_compound_line")

    def test_37_insert_polylines_segments_test1(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm",     "p1",     "0mm"],
                       ["-p1",     "0mm",    "0mm"],
                       ["-p1/2",   "-p1/2",  "0mm"],
                       ["0mm",     "0mm",    "0mm"]]
        P = prim3D.create_polyline(position_list=test_points,
                                   close_surface=True,
                                   name="PL08_segmented_compound_insert_segment")
        assert P
        start_point = P.start_point
        insert_point = ["90mm", "20mm", "0mm"]
        assert P.insert_segment(position_list=[start_point, insert_point])

    def test_38_insert_polylines_segments_test2(self):
        prim3D = self.aedtapp.modeler.primitives
        self.aedtapp["p1"] = "100mm"
        self.aedtapp["p2"] = "71mm"
        test_points = [["0mm",     "p1",     "0mm"],
                       ["-p1",     "0mm",    "0mm"],
                       ["-p1/2",   "-p1/2",  "0mm"],
                       ["0mm",     "0mm",    "0mm"]]

        P = prim3D.create_polyline(position_list=test_points,
                                   close_surface=False,
                                   name="PL08_segmented_compound_insert_arc")
        start_point = P.vertex_positions[1]
        insert_point1 = ["90mm", "20mm", "0mm"]
        insert_point2 = [40, 40, 0]

        P.insert_segment(position_list=[start_point, insert_point1, insert_point2], segment="Arc")

    def test_39_modify_crossection(self):

        primitives = self.aedtapp.modeler.primitives
        P = self.aedtapp.modeler.primitives.create_polyline(position_list=[[34.1004, 14.1248, 0],
                                                                           [27.646, 16.7984, 0],
                                                                           [24.9725, 10.3439, 0]],
                                                            name="Rotor_Subtract_25_0",
                                                            matname="copper")
        P1 = P.clone()
        P2 = P.clone()
        P3 = P.clone()
        P4 = P.clone()

        P1.set_crosssection_properties(type="Line", width="1mm")
        P2.set_crosssection_properties(type="Circle", width="1mm", num_seg=5)
        P3.set_crosssection_properties(type="Rectangle", width="1mm", height="1mm")
        P4.set_crosssection_properties(type="Isosceles Trapezoid", width="1mm", height="1mm", topwidth="4mm")

        assert primitives.objects[P.id].object_type == "Line"
        assert primitives.objects[P1.id].object_type == "Sheet"
        assert primitives.objects[P2.id].is3d
        assert primitives.objects[P3.id].is3d
        assert primitives.objects[P4.id].is3d
        assert primitives.objects[P2.id].object_type == "Solid"
        assert primitives.objects[P3.id].object_type == "Solid"
        assert primitives.objects[P4.id].object_type == "Solid"

    def test_40_remove_vertex_from_polyline(self):

        primitives = self.aedtapp.modeler.primitives
        if not primitives["PL06_segmented_compound_line"]:
            self.test_36_compound_polylines_segments()

        test_points = [["0mm",     "p1",     "0mm"],
                       ["-p1",     "0mm",    "0mm"],
                       ["-p1/2",   "-p1/2",  "0mm"],
                       ["0mm",     "0mm",    "0mm"]]

        id = primitives.get_obj_id("PL06_segmented_compound_line")
        P = primitives.get_existing_polyline(object_id=id)
        P.remove_vertex(test_points[2])

        P1 = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P1.remove_vertex([0, 1, 2])

        P2 = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2.remove_vertex(["0mm", "1mm", "2mm"])

        P3 = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P3.remove_vertex(["0mm", "1mm", "2mm"], abstol=1e-6)

    def test_41_remove_edges_from_polyline(self):

        primitives = self.aedtapp.modeler.primitives
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_edges(edge_id=0)
        P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P.remove_edges(edge_id=[0, 1])


    def test_42_duplicate_polyline_and_manipulate(self):

        primitives = self.aedtapp.modeler.primitives
        P1 = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        P2 = P1.clone()

        assert P2.id != P1.id

    def test_43_create_bond_wires(self):

        b1 = self.aedtapp.modeler.primitives.create_bondwire([0,0,0], [10,10,2], h1=0.15, h2=0, diameter=0.034, facets=8, matname="copper", name="jedec51")
        assert b1
        b2 = self.aedtapp.modeler.primitives.create_bondwire([0,0,0], [10,10,2], h1=0.15, h2=0, diameter=0.034, bond_type=1,  matname="copper", name="jedec41")
        assert b2
        b2 = self.aedtapp.modeler.primitives.create_bondwire([0,0,0], [10,10,2], h1=0.15, h2=0, diameter=0.034, bond_type=2,  matname="copper", name="jedec41")
        assert b2
        b2 = self.aedtapp.modeler.primitives.create_bondwire([0,0,0], [10,10,2], h1=0.15, h2=0, diameter=0.034, bond_type=3,  matname="copper", name="jedec41")
        assert b2 == False

    def test_44_create_group(self):
        assert self.aedtapp.modeler.create_group(["jedec51","jedec41"],"mygroup")
        assert self.aedtapp.modeler.ungroup("mygroup")

    def test_45_flatten_assembly(self):
        assert self.aedtapp.modeler.flatten_assembly()

    def test_46_solving_volume(self):
        vol = self.aedtapp.modeler.get_solving_volume()
        assert len(vol) == 9

    def test_46_lines(self):
        assert self.aedtapp.modeler.vertex_data_of_lines()

    def test_47_get_edges_on_bunding_box(self):
        self.aedtapp.close_project(name=self.aedtapp.project_name, saveproject=False)
        self.aedtapp.load_project(self.test_99_project)
        self.prim._refresh_all_ids()
        edges = self.prim.get_edges_on_bunding_box(['Port1', 'Port2'], return_colinear=True, tol=1e-6)
        assert edges == [5219, 5183]
        edges = self.prim.get_edges_on_bunding_box(['Port1', 'Port2'], return_colinear=False, tol=1e-6)
        assert edges == [5237, 5255, 5273, 5291]

    @pytest.mark.skipif(config["build_machine"] == True,
                        reason="Skipped because SpaceClaim is not installed on Build Machine")
    def test_48_import_space_claim(self):
        self.aedtapp.insert_design("SCImport")
        assert self.aedtapp.modeler.import_spaceclaim_document(os.path.join(self.local_scratch.path, scdoc))
        assert len(self.aedtapp.modeler.primitives.objects) == 1

    def test_49_import_step(self):
        self.aedtapp.insert_design("StepImport")
        assert self.aedtapp.modeler.import_3d_cad(os.path.join(self.local_scratch.path, step))
        assert len(self.aedtapp.modeler.primitives.objects) == 1
