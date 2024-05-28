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
    def init(self, desktop):
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

    def test_01_template(self, add_app):
        script_path = os.path.join(pyaedt.workflows.templates.__path__[0], "toolkit_template.py")
        aedtapp = add_app(application=pyaedt.Hfss, project_name="workflow_test")
        os.environ["PYAEDT_TEST_CONFIG"] = "1"
        subprocess.Popen([sys.executable, script_path],
                         env=os.environ.copy(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).wait()
        assert len(aedtapp.modeler.object_list) == 1
        aedtapp.close_project(aedtapp.project_name)

    def test_02_hfss_push(self, add_app):
        aedtapp = add_app(project_name=push_project, subfolder=test_subfolder)

        script_path = os.path.join(pyaedt.workflows.hfss.__path__[0], "push_excitation_from_file.py")

        # No choice
        test_config = {
            "file_path": os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv"),
            "choice": ""
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)
        subprocess.Popen([sys.executable, script_path],
                         env=os.environ.copy(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).wait()
        aedtapp.save_project()
        assert not aedtapp.design_datasets

        # Correct choice
        test_config = {
            "file_path": os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv"),
            "choice": "1:1"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        subprocess.Popen([sys.executable, script_path],
                         env=os.environ.copy(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).wait()
        aedtapp.save_project()
        assert aedtapp.design_datasets
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_q3d(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        script_path = os.path.join(pyaedt.workflows.hfss3dlayout.__path__[0], "export_to_3d.py")

        test_config = {
            "choice": "Export to Q3D"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        subprocess.Popen([sys.executable, script_path], env=os.environ.copy()).wait()

        assert os.path.isfile(aedtapp.project_file[:-5] + "_Q3D.aedt")
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_Q3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_icepak(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        script_path = os.path.join(pyaedt.workflows.hfss3dlayout.__path__[0], "export_to_3d.py")

        test_config = {
            "choice": "Export to Icepak"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        subprocess.Popen([sys.executable, script_path], env=os.environ.copy()).wait()

        assert os.path.isfile(aedtapp.project_file[:-5] + "_IPK.aedt")
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_IPK")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_maxwell(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        script_path = os.path.join(pyaedt.workflows.hfss3dlayout.__path__[0], "export_to_3d.py")

        test_config = {
            "choice": "Export to Maxwell 3D"
        }
        os.environ["PYAEDT_TEST_CONFIG"] = json.dumps(test_config)

        subprocess.Popen([sys.executable, script_path], env=os.environ.copy()).wait()

        assert os.path.isfile(aedtapp.project_file[:-5] + "_M3D.aedt")
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_M3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_04_project_report(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout, project_name="workflow_pdf")

        script_path = os.path.join(pyaedt.workflows.project.__path__[0], "create_report.py")

        os.environ["PYAEDT_TEST_CONFIG"] = "1"

        subprocess.Popen([sys.executable, script_path],
                         env=os.environ.copy(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).wait()
        assert os.path.isfile(os.path.join(aedtapp.working_directory, "AEDT_Results.pdf"))
        aedtapp.close_project(aedtapp.project_name)
