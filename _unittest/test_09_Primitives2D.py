#!/ekm/software/anaconda3/bin/python
# Import required modules
from _unittest.conftest import BasisTest
from _unittest.conftest import pyaedt_unittest_check_desktop_error
from pyaedt import Maxwell2d
from pyaedt.application.Design import DesignCache
from pyaedt.modeler.Primitives import Polyline

# Setup paths for module imports

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self, design_name="2D_Primitives", solution_type="TransientXY", application=Maxwell2d
        )
        self.cache = DesignCache(self.aedtapp)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def create_rectangle(self, name=None):
        if not name:
            name = "MyRectangle"
        if self.aedtapp.modeler[name]:
            self.aedtapp.modeler.delete(name)
        o = self.aedtapp.modeler.create_rectangle([5, 3, 0], [4, 5], name=name)
        return o

    @pyaedt_unittest_check_desktop_error
    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_rectangle(udp, [5, 3], name="Rectangle1", matname="copper")
        assert isinstance(o.id, int)
        assert o.solve_inside

    @pyaedt_unittest_check_desktop_error
    def test_03_create_circle(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o1 = self.aedtapp.modeler.create_circle(udp, 3, 0, name="Circle1", matname="copper")
        assert isinstance(o1.id, int)
        o2 = self.aedtapp.modeler.create_circle(udp, 3, 8, name="Circle2", matname="copper")
        assert isinstance(o2.id, int)

    @pyaedt_unittest_check_desktop_error
    def test_04_create_ellipse(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o = self.aedtapp.modeler.create_ellipse(udp, 3, 2, name="Ellipse1", matname="copper")
        assert isinstance(o.id, int)

    @pyaedt_unittest_check_desktop_error
    def test_05_create_poly(self):
        udp = [self.aedtapp.modeler.Position(0, 0, 0), self.aedtapp.modeler.Position(10, 5, 0)]
        o = self.aedtapp.modeler.create_polyline(udp, name="Ellipse1", matname="copper")
        assert isinstance(o, Polyline)

    @pyaedt_unittest_check_desktop_error
    def test_chamfer_vertex(self):
        o = self.create_rectangle("Rectangle1")
        o.vertices[0].chamfer()

    @pyaedt_unittest_check_desktop_error
    def test_fillet_vertex(self):
        o = self.create_rectangle("Rectangle1")
        o.vertices[0].fillet()

    @pyaedt_unittest_check_desktop_error
    def test_06_create_region(self):
        if self.aedtapp.modeler["Region"]:
            self.aedtapp.modeler.delete("Region")
        assert "Region" not in self.aedtapp.modeler.object_names
        region = self.aedtapp.modeler.create_region([100, 100, 100, 100])
        assert region.solve_inside
        assert region.model
        assert region.display_wireframe
        assert region.object_type == "Sheet"
        assert region.solve_inside

        region = self.aedtapp.modeler.create_region([100, 100, 100, 100, 100, 100])
        assert not region

    # TODO Implement parametrize
    """
    @pytest.mark.parametrize("material", ["ceramic_material", # material not in library
                                        "steel_stainless"])  # material already in library
    @pyaedt_unittest_check_desktop_error
    def test_07_assign_material(self, material):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material
    """

    @pyaedt_unittest_check_desktop_error
    def test_07_assign_material_ceramic(self, material="ceramic_material"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material

    @pyaedt_unittest_check_desktop_error
    def test_07_assign_material(self, material="steel_stainless"):
        self.aedtapp.assign_material(["Rectangle1"], material)
        assert self.aedtapp.modeler["Rectangle1"].material_name == material
