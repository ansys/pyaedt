import os
import pytest
import time
# Setup paths for module imports
from .conftest import scratch_path
import gc

# Import required modules
from pyaedt import Hfss3dLayout
from pyaedt.generic.filesystem import Scratch

# Input Data and version for the test

test_project_name = "Coax_HFSS"


class Test3DLayout:
    def setup_class(self):
        self.aedtapp = Hfss3dLayout()

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        #self.local_scratch.remove()
        gc.collect()

    def test_01_creatematerial(self):
        mymat = self.aedtapp.materials.creatematerial("myMaterial")
        assert mymat.set_property_value(mymat.PropName.Permittivity, 4.1)
        assert mymat.set_property_value("Conductivity", 100)
        assert mymat.set_property_value("Young's Modulus", 1e10)
        assert mymat.update()

    def test_02_add_layer_to_stackup(self):
        s1 = self.aedtapp.modeler.layers.add_layer("Signal3", "signal", "0.035mm", "0mm")
        d2 = self.aedtapp.modeler.layers.add_layer("Diel1", "dielectric", "1mm", "0.035mm", "myMaterial")
        s3 = self.aedtapp.modeler.layers.add_layer("Signal1", "signal", "0.035mm", "1.035mm")
        assert d2.material == "myMaterial"
        assert s1.thickness == "0.035mm"
        assert s3.type == "signal"

    def test_03_create_circle(self):
        n1 = self.aedtapp.modeler.primitives.create_circle("Signal1", 0, 5, 80, "mycircle")
        assert n1 == "mycircle"

    def test_04_create_create_rectangle(self):
        n2 = self.aedtapp.modeler.primitives.create_rectangle("Signal1", 0, 0, 6, 8, 3, 2, "myrectangle")
        assert n2 == "myrectangle"

    def test_05_subtract(self):
        assert self.aedtapp.modeler.subtract("mycircle", "myrectangle")

    def test_06_unite(self):
        n1 = self.aedtapp.modeler.primitives.create_circle("Signal1", 0, 5, 8, "mycircle2")
        n2 = self.aedtapp.modeler.primitives.create_rectangle("Signal1", 0, 0, 6, 8, 3, 2, "myrectangle2")
        assert self.aedtapp.modeler.unite([n1, n2])

    def test_07_intersect(self):
        n1 = self.aedtapp.modeler.primitives.create_circle("Signal1", 0, 5, 8, "mycircle3")
        n2 = self.aedtapp.modeler.primitives.create_rectangle("Signal1", 0, 0, 6, 8, 3, 2, "myrectangle3")
        assert self.aedtapp.modeler.intersect([n1, n2])

    def test_08_objectlist(self):
        a = self.aedtapp.modeler.primitives.geometries
        assert len(a) > 0

    def test_09_modify_padstack(self):
        pad_0 = self.aedtapp.modeler.primitives.padstacks["PlanarEMVia"]
        assert self.aedtapp.modeler.primitives.padstacks["PlanarEMVia"].plating != 55
        pad_0.plating = 55
        pad_0.update()
        self.aedtapp.modeler.primitives.init_padstacks()
        assert self.aedtapp.modeler.primitives.padstacks["PlanarEMVia"].plating == '55'

    def test_10_create_padstack(self):
        pad1 = self.aedtapp.modeler.primitives.new_padstack("My_padstack2")
        hole1 = pad1.add_hole()
        pad1.add_layer("Start", pad_hole= hole1, thermal_hole=hole1)
        hole2 = pad1.add_hole(holetype="Rct", sizes=[0.5,0.8])
        pad1.add_layer("Default", pad_hole=hole2, thermal_hole=hole2)
        pad1.add_layer("Stop", pad_hole= hole1, thermal_hole=hole1)
        pad1.hole.sizes=['0.8mm']
        pad1.plating = 70
        assert pad1.create()

    def test_11_create_via(self):
        via = self.aedtapp.modeler.primitives.create_via("My_padstack2", x=0, y=0)
        assert type(via) is str
        via = self.aedtapp.modeler.primitives.create_via("My_padstack2", x=10, y=10, name="Via123", netname="VCC")
        assert via == "Via123"

    def test_12_create_line(self):
        line = self.aedtapp.modeler.primitives.create_line("Signal3",lw=1,x=[0,10,20],y=[0,30,30],name="line1", netname="VCC")
        assert line == "line1"

    def test_13a_create_edge_port(self):
        assert self.aedtapp.create_edge_port("line1",3, False)
        assert self.aedtapp.create_edge_port("line1",0, True)

    def test_14a_create_coaxial_port(self):
        assert self.aedtapp.create_coax_port("Via123","Signal3","Signal1", 10, 10, 10,10)

    def test_14_create_setup(self):
        setup_name = "RFBoardSetup"
        setup = self.aedtapp.create_setup(setupname=setup_name)
        assert setup.name == self.aedtapp.existing_analysis_setups[0]

    def test_15_edit_setup(self):
        setup_name = "RFBoardSetup2"
        setup2 = self.aedtapp.create_setup(setupname=setup_name)
        setup2.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData'][
            'AdaptiveFrequency'] = "1GHz"
        setup2.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData']['MaxPasses'] = 23
        setup2.props['AdvancedSettings']['OrderBasis'] = 2
        setup2.props['PercentRefinementPerPass'] = 17
        assert setup2.update()

    def test_16_disable_enable_setup(self):
        setup_name = "RFBoardSetup3"
        setup3 = self.aedtapp.create_setup(setupname=setup_name)
        setup3.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData'][
            'MaxPasses'] = 1
        assert setup3.update()
        assert setup3.disable()
        assert setup3.enable()

    def test_17_get_setup(self):
        setup4 = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
        setup4.props['PercentRefinementPerPass'] = 37
        setup4.props['AdaptiveSettings']['SingleFrequencyDataList']['AdaptiveFrequencyData'][
            'MaxPasses'] = 44
        assert setup4.update()
        assert setup4.disable()
        assert setup4.enable()

    def test_18_add_sweep(self):
        setup_name = "RFBoardSetup"
        assert self.aedtapp.create_frequency_sweep(setupname=setup_name,
                                                   unit='GHz', freqstart=1, freqstop=10, num_of_freq_points=1001,
                                                   sweepname="RFBoardSweep1", sweeptype="interpolating",
                                                   interpolation_tol_percent=0.2, interpolation_max_solutions=255,
                                                   save_fields=False, use_q3d_for_dc=False)
        assert self.aedtapp.create_frequency_sweep(setupname=setup_name,
                                                   unit='GHz', freqstart=1, freqstop=10, num_of_freq_points=12,
                                                   sweepname="RFBoardSweep2", sweeptype="discrete",
                                                   interpolation_tol_percent=0.4, interpolation_max_solutions=255,
                                                   save_fields=True, save_rad_fields_only=True, use_q3d_for_dc=True)

    def test_19_validate(self):
        assert self.aedtapp.validate_full_design()
        self.aedtapp.delete_port("Port3")
        assert self.aedtapp.validate_full_design(ports=3)

    def test_19A_analyse_setup(self):
        assert self.aedtapp.analyze_setup("RFBoardSetup3")

    def test_19B_export_touchsthone(self):
        filename = os.path.join(scratch_path, 'touchstone.s2p')
        assert self.aedtapp.export_touchstone("RFBoardSetup3", "Last Adaptive",
                                              filename, [], [])
        assert os.path.exists(filename)

    def test_19_export_to_hfss(self):
        with Scratch(scratch_path) as local_scratch:
            filename = 'export_to_hfss_test'
            file_fullname = os.path.join(local_scratch.path, filename)
            setup = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
            assert setup.export_to_hfss(file_fullname=file_fullname)
            time.sleep(2)  # wait for the export operation to finish

    def test_20_set_export_touchstone(self):
        assert self.aedtapp.set_export_touchstone(True)
        assert self.aedtapp.set_export_touchstone(False)


if __name__ == '__main__':
    pytest.main()
