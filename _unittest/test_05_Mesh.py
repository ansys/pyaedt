import os
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Setup paths for module imports
from _unittest.conftest import scratch_path
import gc
# Import required modules
from pyaedt import Hfss, Maxwell3d
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_HFSS"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss()

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_assign_model_resolution(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension,
                                                         0, "inner")
        self.aedtapp.mesh.assign_model_resolution(o, 1e-4,"ModelRes1")
        assert "ModelRes1" in [i.name for i in self.aedtapp.mesh.meshoperations]
        mr2 = self.aedtapp.mesh.assign_model_resolution(o.faces[0], 1e-4,"ModelRes2")
        assert not mr2

    def test_assign_surface_mesh(self):
        udp = self.aedtapp.modeler.Position(10, 10, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension,
                                                         0, "surface")
        surface = self.aedtapp.mesh.assign_surface_mesh(o.id, 3,"Surface")
        assert "Surface" in [i.name for i in  self.aedtapp.mesh.meshoperations]
        assert surface.props["SliderMeshSettings"] == 3

    def test_assign_surface_mesh_manual(self):
        udp = self.aedtapp.modeler.Position(20, 20, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension,
                                                         0, "surface_manual")
        surface = self.aedtapp.mesh.assign_surface_mesh_manual(
            o.id, 1e-6, aspect_ratio=3,meshop_name="Surface_Manual")
        assert "Surface_Manual" in [i.name for i in  self.aedtapp.mesh.meshoperations]
        assert surface.props["SurfDev"] ==  1e-6
        assert surface.props["AspectRatioChoice"]

    def test_assign_surface_priority(self):
        surface = self.aedtapp.mesh.assign_surf_priority_for_tau(["surface", "surface_manual"], 1)
        assert surface

    def test_delete_mesh_ops(self):
        surface = self.aedtapp.mesh.delete_mesh_operations("surface")
        assert surface

    def test_curvature_extraction(self):
        self.aedtapp.solution_type = "SBR+"
        assert self.aedtapp.mesh.assign_curvature_extraction("inner")

    def test_maxwell_mesh(self):
        m3d = Maxwell3d()
        o = m3d.modeler.primitives.create_box([0,0,0], [10,10,10], name="Box_Mesh")
        assert m3d.mesh.assign_rotational_layer(o.name, meshop_name="Rotational")
        assert m3d.mesh.assign_edge_cut(o.name, meshop_name="Edge")
        assert m3d.mesh.assign_density_control(
            o.name, maxelementlength=10000, meshop_name="Density")
