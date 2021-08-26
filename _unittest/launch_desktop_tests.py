# Import required modules
from pyaedt import Hfss, Maxwell2d, Maxwell3d, Q2d, Q3d, Simplorer, Hfss3dLayout, Icepak, Circuit, Mechanical

def run_desktop_tests():
    aedtapp = Mechanical(specified_version="2021.1")
    assert aedtapp.design_type == "Mechanical"
    assert aedtapp.solution_type == "Thermal"
    aedtapp.close_desktop()

    aedtapp = Circuit(specified_version="2021.1")
    assert aedtapp.design_type == "Circuit Design"
    assert aedtapp.solution_type == "NexximLNA"
    aedtapp.close_desktop()

    aedtapp = Icepak(specified_version="2021.1")
    assert aedtapp.design_type == "Icepak"
    assert aedtapp.solution_type == "SteadyState"
    aedtapp.close_desktop()

    aedtapp = Hfss3dLayout(specified_version="2021.1")
    assert aedtapp.design_type == "HFSS 3D Layout Design"
    assert aedtapp.solution_type == "HFSS3DLayout"
    aedtapp.close_desktop()

    aedtapp = Simplorer(specified_version="2021.1")
    assert aedtapp.design_type == "Twin Builder"
    assert aedtapp.solution_type == "TR"
    aedtapp.close_desktop()
    pass

    aedtapp = Q2d(specified_version="2021.1")
    assert aedtapp.design_type == "2D Extractor"
    assert aedtapp.solution_type == "Open"
    aedtapp.close_desktop()
    pass

    aedtapp = Q3d(specified_version="2021.1")
    assert aedtapp.design_type == "Q3D Extractor"
    assert aedtapp.solution_type == "Matrix"
    aedtapp.close_desktop()
    pass

    aedtapp = Maxwell2d(specified_version="2021.1")
    aedtapp.design_type == "Maxwell 2D"
    aedtapp.solution_type == "Magnetostatic"
    aedtapp.close_desktop()

    aedtapp = Hfss(specified_version="2021.1")
    assert aedtapp.design_type == "HFSS"
    assert aedtapp.solution_type == "DrivenModal"
    aedtapp.close_desktop()
    pass

    aedtapp = Maxwell3d(specified_version="2021.1")
    assert aedtapp.design_type == "Maxwell 3D"
    assert aedtapp.solution_type == "Magnetostatic"
    aedtapp.close_desktop()
    pass
