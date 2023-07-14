# Import required modules
from _unittest.conftest import BasisTest
from _unittest.conftest import NONGRAPHICAL
from _unittest.conftest import config
from _unittest.conftest import desktop_version

from pyaedt import Circuit
from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Maxwell2d
from pyaedt import Maxwell3d
from pyaedt import Mechanical
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import TwinBuilder

try:
    import pytest
except ImportError:  # pragma: no cover
    import _unittest_ironpython.conf_unittest as pytest


@pytest.mark.skipif(config["skip_desktop_test"], reason="Desktop tests are not selected by default.")
class TestClass(BasisTest, object):
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    def test_run_desktop_mechanical(self):
        aedtapp = Mechanical(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Mechanical"
        assert aedtapp.solution_type == "Steady-State Thermal"
        aedtapp.solution_type = "Modal"
        assert aedtapp.solution_type == "Modal"
        aedtapp.close_desktop()

    def test_run_desktop_circuit(self):
        aedtapp = Circuit(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Circuit Design"
        assert aedtapp.solution_type == "NexximLNA"
        aedtapp.close_desktop()

    def test_run_desktop_icepak(self):
        aedtapp = Icepak(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Icepak"
        assert aedtapp.solution_type == "SteadyState"
        aedtapp.close_desktop()

    def test_run_desktop_hfss3dlayout(self):
        aedtapp = Hfss3dLayout(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "HFSS 3D Layout Design"
        assert aedtapp.solution_type == "HFSS3DLayout"
        aedtapp.close_desktop()

    def test_run_desktop_twinbuilder(self):
        aedtapp = TwinBuilder(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Twin Builder"
        assert aedtapp.solution_type == "TR"
        aedtapp.close_desktop()

    def test_run_desktop_q2d(self):
        aedtapp = Q2d(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "2D Extractor"
        assert aedtapp.solution_type == "Open"
        aedtapp.close_desktop()

    def test_run_desktop_q3d(self):
        aedtapp = Q3d(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Q3D Extractor"
        aedtapp.close_desktop()

    def test_run_desktop_maxwell2d(self):
        aedtapp = Maxwell2d(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Maxwell 2D"
        assert aedtapp.solution_type == "Magnetostatic"
        aedtapp.close_desktop()

    def test_run_desktop_hfss(self):
        aedtapp = Hfss(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "HFSS"
        assert "Modal" in aedtapp.solution_type
        aedtapp.close_desktop()

    def test_run_desktop_maxwell3d(self):
        aedtapp = Maxwell3d(specified_version=desktop_version, non_graphical=NONGRAPHICAL)
        assert aedtapp.design_type == "Maxwell 3D"
        assert aedtapp.solution_type == "Magnetostatic"
        aedtapp.close_desktop()
