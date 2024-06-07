import pytest
import os
import shutil

import pyaedt
from pyaedt.generic.settings import is_linux
# from _unittest_solvers.conftest import local_path as solver_local_path
from _unittest.conftest import local_path

push_project = "push_excitation"
export_3d_project = "export"
twinbuilder_circuit = "TB_test"
report = "report"

test_subfolder = "T45"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, desktop):
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

    def test_01_template(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss, project_name="workflow_test")

        from pyaedt.workflows.templates.extension_template import main
        assert main({"is_test": True})

        assert len(aedtapp.modeler.object_list) == 1
        aedtapp.close_project(aedtapp.project_name)

    def test_02_hfss_push(self, add_app):
        aedtapp = add_app(project_name=push_project, subfolder=test_subfolder)

        from pyaedt.workflows.hfss.push_excitation_from_file import main

        # No choice
        file_path = os.path.join(local_path, "example_models", "T20", "Sinusoidal.csv")
        assert main({"is_test": True, "file_path": file_path, "choice": ""})
        aedtapp.save_project()
        assert not aedtapp.design_datasets

        # Correct choice
        assert main({"is_test": True, "file_path": file_path, "choice": "1:1"})
        aedtapp.save_project()
        assert aedtapp.design_datasets
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_q3d(self, local_scratch, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_q3d.aedt"))

        from pyaedt.workflows.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Q3D"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_q3d_Q3D.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_Q3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_icepak(self, local_scratch, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_icepak.aedt"))

        from pyaedt.workflows.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Icepak"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_icepak_IPK.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_IPK")
        aedtapp.close_project(aedtapp.project_name)

    def test_03_hfss3dlayout_export_3d_maxwell(self, local_scratch, add_app):
        aedtapp = add_app(application=pyaedt.Hfss3dLayout,
                          project_name=export_3d_project,
                          subfolder=test_subfolder)

        aedtapp.save_project(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_maxwell.aedt"))

        from pyaedt.workflows.hfss3dlayout.export_to_3d import main

        assert main({"is_test": True, "choice": "Export to Maxwell 3D"})

        assert os.path.isfile(os.path.join(local_scratch.path, "test_03_hfss3dlayout_export_3d_maxwell_M3D.aedt"))
        aedtapp.close_project(os.path.basename(aedtapp.project_file[:-5]) + "_M3D")
        aedtapp.close_project(aedtapp.project_name)

    def test_04_project_report(self, add_app):
        aedtapp = add_app(application=pyaedt.Hfss,
                          project_name=report,
                          subfolder=test_subfolder)

        from pyaedt.workflows.project.create_report import main

        assert main({"is_test": True})

        assert os.path.isfile(os.path.join(aedtapp.working_directory, "AEDT_Results.pdf"))
        aedtapp.close_project(aedtapp.project_name)

    def test_05_project_import_nastran(self, add_app, local_scratch):
        aedtapp = add_app(application=pyaedt.Hfss, project_name="workflow_nastran")

        from pyaedt.workflows.project.import_nastran import main

        # Non-existing file
        file_path = os.path.join(local_scratch.path, "test_cad_invented.nas")

        assert main({"is_test": True, "file_path": file_path, "lightweight": True, "decimate": 0.0, "planar": True})

        assert len(aedtapp.modeler.object_list) == 0

        file_path = shutil.copy(os.path.join(local_path, "example_models", "T20", "test_cad.nas"),
                                os.path.join(local_scratch.path, "test_cad.nas"))

        assert main({"is_test": True, "file_path": file_path, "lightweight": True, "decimate": 0.0, "planar": True})

        assert len(aedtapp.modeler.object_list) == 3
        aedtapp.close_project(aedtapp.project_name)

    def test_06_project_import_stl(self, add_app, local_scratch):
        aedtapp = add_app(application=pyaedt.Hfss, project_name="workflow_stl")

        from pyaedt.workflows.project.import_nastran import main

        file_path = shutil.copy(os.path.join(local_path, "example_models", "T20", "sphere.stl"),
                                os.path.join(local_scratch.path, "sphere.stl"))

        assert main({"is_test": True, "file_path": file_path, "lightweight": True, "decimate": 0.0, "planar": True})

        assert len(aedtapp.modeler.object_list) == 1
        aedtapp.close_project(aedtapp.project_name)

    @pytest.mark.skipif(is_linux, reason="Not supported in Linux.")
    def test_07_twinbuilder_convert_circuit(self, add_app):
        aedtapp = add_app(application=pyaedt.TwinBuilder,
                          project_name=twinbuilder_circuit,
                          subfolder=test_subfolder)

        from pyaedt.workflows.twinbuilder.convert_to_circuit import main

        assert main({"is_test": True})

        circuit = pyaedt.Circuit()
        assert len(circuit.modeler.schematic.components) == 10
        aedtapp.close_project(aedtapp.project_name)
