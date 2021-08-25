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
            example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
            self.test_project = self.local_scratch.copyfile(example_project)
            self.aedtapp = Hfss(projectname=self.test_project, designname="Cassegrain_", solution_type="SBR+")
            self.source = Hfss(projectname=test_project_name, designname="feeder")

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name,saveproject=False)
        self.local_scratch.remove()
        gc.collect()


    def test_01A_open_source(self):
        assert self.aedtapp.create_sbr_linked_antenna(self.source, target_cs="feederPosition", fieldtype="farfield")
        assert len(self.aedtapp.native_components) == 1

    def test_02_add_parametric_beam(self):
        dict1 = {"polarization": "Vertical"}
        par_beam = self.aedtapp.create_sbr_parametric_beam_antenna(parameters_dict=dict1, antenna_name="TX1")
        assert self.aedtapp.create_sbr_parametric_beam_antenna()
        par_beam.props["NativeComponentDefinitionProvider"]["Unit"] = "in"
        assert par_beam.update()
        assert len(self.aedtapp.native_components) == 3

    def test_03_add_ffd_antenna(self):
        assert self.aedtapp.create_sbr_file_based_antenna(ffd_full_path=os.path.join(local_path, 'example_models', 'test.ffd'))
        assert len(self.aedtapp.native_components) == 4
