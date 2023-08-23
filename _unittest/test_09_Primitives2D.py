#!/ekm/software/anaconda3/bin/python
import pytest

from pyaedt import Maxwell2d
from pyaedt.modeler.cad.polylines import Polyline


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(design_name="2D_Primitives_2", solution_type="TransientXY", application=Maxwell2d)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def create_rectangle(self, name=None):
        if not name:
            name = "MyRectangle"
        if self.aedtapp.modeler[name]:
            self.aedtapp.modeler.delete(name)
        o = self.aedtapp.modeler.create_rectangle([5, 3, 0], [4, 5], name=name)
        return o

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1", matname="copper")
        assert isinstance(o.id, int)
        assert o.solve_inside

    def test_03_create_circle(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o1 = self.aedtapp.modeler.create_circle(udp, 3, 0, name="Circle1", matname="copper")
        assert isinstance(o1.id, int)
        o2 = self.aedtapp.modeler.create_circle(udp, 3, 8, name="Circle2", matname="copper")
        assert isinstance(o2.id, int)

    def test_04_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_ellipse(udp, 3, 2, name="Ellipse1", matname="copper")
        assert isinstance(o.id, int)

    def test_05_create_poly(self):
        udp = [self.aedtapp.modeler.Position(0, 0, 0), self.aedtapp.modeler.Position(10, 5, 0)]
        o = self.aedtapp.modeler.create_polyline(udp, name="Ellipse1", matname="copper")
        assert isinstance(o, Polyline)

    def test_chamfer_vertex(self):
        o = self.create_rectangle("Rectangle1")
        o.vertices[0].chamfer()

    def test_fillet_vertex(self):
        o = self.create_rectangle("Rectangle1")
        o.vertices[0].fillet()

    def test_06_create_region(self):
        if self.aedtapp.modeler["Region"]:
            self.aedtapp.modeler.delete("Region")
        assert "Region" not in self.aedtapp.modeler.object_names
        assert self.aedtapp.modeler.create_region([20, "50", "100mm", 20], False)
        self.aedtapp.modeler["Region"].delete()
        region = self.aedtapp.modeler.create_region("100", True)
        region.delete()
        region = self.aedtapp.modeler.create_region([100, 100, 100, 100])
        assert region.solve_inside
        assert region.model
        assert region.display_wireframe
        assert region.object_type == "Sheet"
        assert region.solve_inside

        region = self.aedtapp.modeler.create_region([100, 100, 100, 100, 100, 100])
        assert not region

    def test_07_assign_material_ceramic(self, material="Ceramic_material"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material

    def test_07_assign_material(self, material="steel_stainless"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material
