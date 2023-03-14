# Import required modules
from _unittest.conftest import BasisTest
from _unittest.conftest import desktop_version

from pyaedt import Maxwell3d

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name="Test05")

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_assign_model_resolution(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "inner")
        mr1 = self.aedtapp.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
        assert mr1.name in self.aedtapp.odesign.GetChildObject("Mesh").GetChildNames()
        mr1.name = "resolution_test"
        assert "resolution_test" in self.aedtapp.mesh.meshoperations[0].name
        mr1.name = "resolution_test"
        assert self.aedtapp.odesign.GetChildObject("Mesh")
        mr1.props["Model Resolution Length"] = "0.1mm"
        assert (
            self.aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mr1.name).GetPropValue("Model Resolution Length")
            == "0.1mm"
        )
        o2 = self.aedtapp.modeler.create_cylinder(self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "inner")
        mr1.props["Objects"] = [o2.name, o.name]
        if desktop_version >= "2023.1":
            assert len(self.aedtapp.mesh.omeshmodule.GetMeshOpAssignment(mr1.name)) == 2
        mr2 = self.aedtapp.mesh.assign_model_resolution(o.faces[0], 1e-4, "ModelRes2")
        assert not mr2

    def test_assign_surface_mesh(self):
        udp = self.aedtapp.modeler.Position(10, 10, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "surface")
        surface = self.aedtapp.mesh.assign_surface_mesh(o.id, 3, "Surface")
        assert "Surface" in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface.props["Curved Surface Mesh Resolution"] == 3

    def test_assign_surface_mesh_manual(self):
        udp = self.aedtapp.modeler.Position(20, 20, 0)
        coax_dimension = 200
        o = self.aedtapp.modeler.create_cylinder(self.aedtapp.PLANE.XY, udp, 3, coax_dimension, 0, "surface_manual")
        surface = self.aedtapp.mesh.assign_surface_mesh_manual(o.id, 1e-6, aspect_ratio=3, meshop_name="Surface_Manual")
        assert "Surface_Manual" in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface.props["Surface Deviation"] == 1e-6
        surface["Surface Deviation"] = 1e-5
        assert surface.props["Surface Deviation"] == 1e-5
        assert surface.props["Normal Deviation"] == "Default Value"
        surface.props["Aspect Ratio"] = 20
        assert surface.props["Aspect Ratio"] == 20

        cylinder_zx = self.aedtapp.modeler.create_cylinder(
            self.aedtapp.PLANE.ZX, udp, 3, coax_dimension, 0, "surface_manual"
        )
        surface_default_value = self.aedtapp.mesh.assign_surface_mesh_manual(cylinder_zx.id)
        assert surface_default_value.name in [i.name for i in self.aedtapp.mesh.meshoperations]
        assert surface_default_value.props["Surface Deviation"] == "Default Value"
        assert surface_default_value.props["Normal Deviation"] == "Default Value"

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
        m3d = Maxwell3d(specified_version=desktop_version)
        o = m3d.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box_Mesh")
        assert m3d.mesh.assign_rotational_layer(o.name, meshop_name="Rotational")
        assert m3d.mesh.assign_edge_cut(o.name, meshop_name="Edge")
        assert m3d.mesh.assign_density_control(o.name, maxelementlength=10000, meshop_name="Density")
