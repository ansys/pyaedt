import pytest
import os
import shutil

import ansys.aedt.core
from ansys.aedt.core.generic.settings import is_linux
from _unittest.conftest import local_path
from _unittest_solvers.conftest import local_path as solver_local_path

push_project = "push_excitation"
export_3d_project = "export"
twinbuilder_circuit = "TB_test"
report = "report"
fields_calculator = "fields_calculator_solved"
m2d_electrostatic = "maxwell_fields_calculator"

test_subfolder = "T45"
TEST_REVIEW_FLAG = True


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, desktop):
        os.environ["PYAEDT_SCRIPT_PORT"] = str(desktop.port)
        os.environ["PYAEDT_SCRIPT_VERSION"] = desktop.aedt_version_id

    def test_08_configure_a3d(self, local_scratch):
        from ansys.aedt.core.workflows.project.configure_edb import main

        configuration_path = shutil.copy(os.path.join(solver_local_path, "example_models", "T45", "ports.json"),
                                         os.path.join(local_scratch.path, "ports.json"))
        file_path = os.path.join(local_scratch.path, "ANSYS-HSD_V1.aedb")
        local_scratch.copyfolder(os.path.join(solver_local_path, "example_models", "T45", "ANSYS-HSD_V1.aedb"),
                                 file_path)

        edbapp = ansys.aedt.core.Edb(file_path, edbversion="2024.2")
        for i in edbapp.padstack_defs:
            i.GetData().GetLayerNames()
        edbapp.close()
