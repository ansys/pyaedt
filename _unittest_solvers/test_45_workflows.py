import pytest
import json
import os
import sys

import pyaedt
from _unittest_solvers.conftest import local_path as solver_local_path
from _unittest.conftest import local_path
import subprocess

import pyaedt.workflows

push_project = "push_excitation"
export_3d_project = "export"

test_subfolder = "T45"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, desktop, local_scratch):
        self.local_scratch = local_scratch
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

    def test_01_template(self, add_app):
        script_path = os.path.join(pyaedt.workflows.templates.__path__[0], "toolkit_template.py")
        os.environ["PYAEDT_TEST_CONFIG"] = "1"
        add_app(application=pyaedt.Hfss)
        subprocess.Popen([sys.executable, script_path])

    def test_02_hfss_push(self, add_app):
        script_path = os.path.join(pyaedt.workflows.hfss.__path__[0], "push_excitation_from_file.py")

        test_config = {
            "file_path": os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv")
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)
        aedtapp = add_app(project_name=push_project, subfolder=test_subfolder)

        subprocess.Popen([sys.executable, script_path], env=os.environ.copy()).wait()
        aedtapp.save_project()
        assert aedtapp.design_datasets

    def test_03_export_3d(self, add_app, local_scratch):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)
        aedtapp.desktop_class.active_design(project_object=aedtapp.oproject, name=aedtapp.design_name)

        # Q3D
        test_config = {
            "choice": "Export to Q3D"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        from pyaedt.workflows.hfss3dlayout import export_to_3D
        assert os.path.isfile(aedtapp.project_file[:-5] + "_Q3D.aedt")

        # Icepak
        aedtapp.desktop_class.active_design(project_object=aedtapp.oproject, name=aedtapp.design_name)
        test_config = {
            "choice": "Export to Icepak"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        export_to_3D
        assert os.path.isfile(aedtapp.project_file[:-5] + "_Icepak.aedt")
