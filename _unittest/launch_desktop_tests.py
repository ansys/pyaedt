# Import required modules
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


def run_desktop_tests():
    aedtapp = Mechanical(specified_version="2021.2")
    assert aedtapp.design_type == "Mechanical"
    assert aedtapp.solution_type == "Thermal"
    aedtapp.close_desktop()

    aedtapp = Circuit(specified_version="2021.2")
    assert aedtapp.design_type == "Circuit Design"
    assert aedtapp.solution_type == "NexximLNA"
    aedtapp.close_desktop()

    aedtapp = Icepak(specified_version="2021.2")
    assert aedtapp.design_type == "Icepak"
    assert aedtapp.solution_type == "SteadyState"
    aedtapp.close_desktop()

    aedtapp = Hfss3dLayout(specified_version="2021.2")
    assert aedtapp.design_type == "HFSS 3D Layout Design"
    assert aedtapp.solution_type == "HFSS3DLayout"
    aedtapp.close_desktop()

    aedtapp = TwinBuilder(specified_version="2021.2")
    assert aedtapp.design_type == "Twin Builder"
    assert aedtapp.solution_type == "TR"
    aedtapp.close_desktop()

    aedtapp = Q2d(specified_version="2021.2")
    assert aedtapp.design_type == "2D Extractor"
    assert aedtapp.solution_type == "Open"
    aedtapp.close_desktop()

    aedtapp = Q3d(specified_version="2021.2")
    assert aedtapp.design_type == "Q3D Extractor"
    assert aedtapp.solution_type == "Matrix"
    aedtapp.close_desktop()

    aedtapp = Maxwell2d(specified_version="2021.2")
    assert aedtapp.design_type == "Maxwell 2D"
    assert aedtapp.solution_type == "Magnetostatic"
    aedtapp.close_desktop()

    aedtapp = Hfss(specified_version="2021.2")
    assert aedtapp.design_type == "HFSS"
    assert "Modal" in aedtapp.solution_type
    aedtapp.close_desktop()

    aedtapp = Maxwell3d(specified_version="2021.2")
    assert aedtapp.design_type == "Maxwell 3D"
    assert aedtapp.solution_type == "Magnetostatic"
    aedtapp.close_desktop()


if __name__ == "__main__":
    run_desktop_tests()
