from _unittest.conftest import config
import pytest

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
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(config["skip_desktop_test"], reason="Desktop tests are not selected by default.")
class TestClass:
    def test_run_desktop_mechanical(self):
        aedtapp = Mechanical()
        assert aedtapp.design_type == "Mechanical"
        assert aedtapp.solution_type == "Steady-State Thermal"
        aedtapp.solution_type = "Modal"
        assert aedtapp.solution_type == "Modal"

    def test_run_desktop_circuit(self):
        aedtapp = Circuit()
        assert aedtapp.design_type == "Circuit Design"
        assert aedtapp.solution_type == "NexximLNA"

    def test_run_desktop_icepak(self):
        aedtapp = Icepak()
        assert aedtapp.design_type == "Icepak"
        assert aedtapp.solution_type == "SteadyState"

    def test_run_desktop_hfss3dlayout(self):
        aedtapp = Hfss3dLayout()
        assert aedtapp.design_type == "HFSS 3D Layout Design"
        assert aedtapp.solution_type == "HFSS3DLayout"

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_run_desktop_twinbuilder(self):
        aedtapp = TwinBuilder()
        assert aedtapp.design_type == "Twin Builder"
        assert aedtapp.solution_type == "TR"

    def test_run_desktop_q2d(self):
        aedtapp = Q2d()
        assert aedtapp.design_type == "2D Extractor"
        assert aedtapp.solution_type == "Open"

    def test_run_desktop_q3d(self):
        aedtapp = Q3d()
        assert aedtapp.design_type == "Q3D Extractor"

    def test_run_desktop_maxwell2d(self):
        aedtapp = Maxwell2d()
        assert aedtapp.design_type == "Maxwell 2D"
        assert aedtapp.solution_type == "Magnetostatic"

    def test_run_desktop_hfss(self):
        aedtapp = Hfss()
        assert aedtapp.design_type == "HFSS"
        assert "Modal" in aedtapp.solution_type

    def test_run_desktop_maxwell3d(self):
        aedtapp = Maxwell3d()
        assert aedtapp.design_type == "Maxwell 3D"
        assert aedtapp.solution_type == "Magnetostatic"
