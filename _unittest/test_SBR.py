import os
# Setup paths for module imports
from _unittest.conftest import scratch_path, local_path
import gc
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

test_project_name = "Cassegrain"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            example_project = os.path.join(
                local_path, 'example_models', test_project_name + '.aedt')
            self.test_project = self.local_scratch.copyfile(example_project)
            self.aedtapp = Hfss(projectname=self.test_project,
                                designname="Cassegrain_", solution_type="SBR+")
            self.source = Hfss(projectname=test_project_name, designname="feeder")

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name,saveproject=False)
        self.local_scratch.remove()
        gc.collect()

    def test_01A_open_source(self):
        assert self.aedtapp.create_sbr_linked_antenna(
            self.source, target_cs="feederPosition", fieldtype="farfield")
        assert len(self.aedtapp.native_components) == 1

    def test_02_add_antennas(self):
        dict1 = {"polarization": "Horizontal"}
        par_beam = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ParametricBeam, parameters_dict=dict1, antenna_name="TX1")
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ConicalHorn, parameters_dict=dict1, antenna_name="RX1")
        par_beam.native_properties["Unit"] = "in"
        assert par_beam.update()
        assert len(self.aedtapp.native_components) == 3
        assert self.aedtapp.set_sbr_txrx_settings({"TX1":"RX1"})
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.CrossDipole, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.HalfWaveDipole, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.HorizontalDipole, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ParametricSlot, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.PyramidalHorn, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ShortDipole, use_current_source_representation=True)
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True)
        toberemoved= self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireDipole, use_current_source_representation=True)
        l = len(self.aedtapp.native_components)
        toberemoved.delete()
        assert len(self.aedtapp.native_components) == l-1
        array = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True)
        array.native_properties['Array Length In Wavelength'] = "10"
        assert array.update()

    def test_03_add_ffd_antenna(self):
        assert self.aedtapp.create_sbr_file_based_antenna(
            ffd_full_path=os.path.join(local_path, 'example_models', 'test.ffd'))
