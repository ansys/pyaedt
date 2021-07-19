import os
# Setup paths for module imports
from .conftest import scratch_path, local_path, desktop_version
import gc
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
import pytest

test_project_name = "Cassegrain"


class TestHFSS:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
            self.test_project = self.local_scratch.copyfile(example_project)
            self.aedtapp = Hfss(projectname=self.test_project, designname="Cassegrain_", solution_type="SBR+", specified_version=desktop_version)
            self.source = Hfss(projectname=test_project_name, designname="feeder", specified_version=desktop_version)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name,saveproject=False)
        self.local_scratch.remove()
        gc.collect()


    @pytest.mark.skip(reason="Issue with example project")
    def test_01A_open_source(self):
         assert self.aedtapp.create_sbr_linked_antenna(self.source, target_cs="feederPosition", fieldtype="farfield")
