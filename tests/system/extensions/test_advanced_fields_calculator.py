# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import asdict
import os
from pathlib import Path
import shutil
import tkinter

from ansys.aedt.core import Hfss
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.project.advanced_fields_calculator import AdvancedFieldsCalculatorExtension
from ansys.aedt.core.extensions.project.advanced_fields_calculator import AdvancedFieldsCalculatorExtensionData
from ansys.aedt.core.extensions.project.advanced_fields_calculator import main
from ansys.aedt.core.extensions.templates.template_get_started import ExtensionData
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from tests.system.extensions.conftest import desktop_version
from tests.system.extensions.conftest import local_path as extensions_local_path

fields_calculator = "fields_calculator_solved"
test_subfolder = "T45"


def test_09_advanced_fields_calculator_general(add_app, tmp_path):
    aedtapp = add_app(application=Q3d, project_name=fields_calculator, subfolder=test_subfolder)

    initial_catalog = len(aedtapp.post.fields_calculator.expression_names)
    example_file = os.path.join(
        extensions_local_path, "example_models", test_subfolder, "expression_catalog_custom.toml"
    )
    new_catalog = aedtapp.post.fields_calculator.load_expression_file(example_file)
    # assert initial_catalog != len(new_catalog)
    assert new_catalog == aedtapp.post.fields_calculator.expression_catalog
    # assert not aedtapp.post.fields_calculator.add_expression("e_field_magnitude", "Polyline1")
    # assert not aedtapp.post.fields_calculator.load_expression_file("invented.toml")

    # from ansys.aedt.core.extensions.project.advanced_fields_calculator import main

    DATA = AdvancedFieldsCalculatorExtensionData(
        setup="Setup1 : LastAdaptive",
        calculation="voltage_drop" if desktop_version <= "2024.2" else "voltage_drop_2025",
        assignments=["Face9", "inner"],
    )
    # aedtapp = add_app(application=Q3d, project_name=fields_calculator, subfolder=test_subfolder)

    # Set the working directory to the temporary path
    os.chdir(tmp_path)
    expression_catalog_path = Path(
        extensions_local_path, "example_models", test_subfolder, "expression_catalog_custom.toml"
    )
    shutil.copy(expression_catalog_path, tmp_path)

    # extension = AdvancedFieldsCalculatorExtension(withdraw=True)

    # tkinter.mainloop()

    assert main(DATA)

    # if desktop_version > "2024.2":
    #     assert main(
    #         {
    #             "is_test": True,
    #             "setup": "Setup1 : LastAdaptive",
    #             "calculation": "voltage_drop_2025",
    #             "assignment": ["Face9", "inner"],
    #         }
    #     )
    # else:
    #     assert main(
    #         {
    #             "is_test": True,
    #             "setup": "Setup1 : LastAdaptive",
    #             "calculation": "voltage_drop",
    #             "assignment": ["Face9", "inner"],
    #         }
    #     )
    # main(data)
    # assert len(aedtapp.post.ofieldsreporter.GetChildNames()) == 2

    # initial_catalog = len(aedtapp.post.fields_calculator.expression_names)
    # example_file = os.path.join(
    #     extensions_local_path, "example_models", test_subfolder, "expression_catalog_custom.toml"
    # )
    # new_catalog = aedtapp.post.fields_calculator.load_expression_file(example_file)
    # assert initial_catalog != len(new_catalog)
    # assert new_catalog == aedtapp.post.fields_calculator.expression_catalog
    # assert not aedtapp.post.fields_calculator.add_expression("e_field_magnitude", "Polyline1")
    # assert not aedtapp.post.fields_calculator.load_expression_file("invented.toml")

    # from ansys.aedt.core.extensions.project.advanced_fields_calculator import main

    # if desktop_version > "2024.2":
    #     assert main(
    #         {
    #             "is_test": True,
    #             "setup": "Setup1 : LastAdaptive",
    #             "calculation": "voltage_drop_2025",
    #             "assignment": ["Face9", "inner"],
    #         }
    #     )
    # else:
    #     assert main(
    #         {
    #             "is_test": True,
    #             "setup": "Setup1 : LastAdaptive",
    #             "calculation": "voltage_drop",
    #             "assignment": ["Face9", "inner"],
    #         }
    #     )
    # assert len(aedtapp.post.ofieldsreporter.GetChildNames()) == 2

    # aedtapp.close_project(aedtapp.project_name)

    # aedtapp = add_app(
    #     application=ansys.aedt.core.Maxwell2d,
    #     project_name=m2d_electrostatic,
    #     design_name="e_tangential",
    #     subfolder=test_subfolder,
    # )
    # name = aedtapp.post.fields_calculator.add_expression("e_line", None)
    # assert name
    # assert aedtapp.post.fields_calculator.expression_plot("e_line", "Poly1", [name])

    # assert main(
    #     {"is_test": True, "setup": "MySetupAuto : LastAdaptive", "calculation": "e_line", "assignment": ["Polyl1"]}
    # )

    # aedtapp.close_project(aedtapp.project_name)

    # aedtapp = add_app(
    #     application=ansys.aedt.core.Maxwell2d,
    #     project_name=m2d_electrostatic,
    #     design_name="stress_tensor",
    #     subfolder=test_subfolder,
    # )
    # name = aedtapp.post.fields_calculator.add_expression("radial_stress_tensor", None)
    # assert name
    # assert aedtapp.post.fields_calculator.expression_plot("radial_stress_tensor", "Polyline1", [name])
    # name = aedtapp.post.fields_calculator.add_expression("tangential_stress_tensor", None)
    # assert name
    # assert aedtapp.post.fields_calculator.expression_plot("tangential_stress_tensor", "Polyline1", [name])

    # aedtapp.close_project(aedtapp.project_name)


# def test_create_sphere_success(add_app, local_scratch):
#     """Test that the extension works correctly when creating a sphere."""
#     DATA = ExtensionData()
#     aedtapp = add_app(application=Hfss, project_name="workflow_template_extension_sphere")

#     assert 0 == len(aedtapp.modeler.object_list)
#     assert main(asdict(DATA))
#     assert 1 == len(aedtapp.modeler.object_list)

#     aedtapp.close_project(aedtapp.project_name)


# def test_load_aedt_file_success(add_app, tmp_path):
#     """Test that the extension works correctly when creating a sphere."""

#     AEDT_PATH = tmp_path / "workflow_template_extension.aedt"
#     DATA = ExtensionData(file_path=AEDT_PATH)
#     OBJECT_NAME = "box"

#     # Create project with a box object
#     app_0 = add_app(application=Hfss)
#     _ = app_0.modeler.create_box([10, 10, 10], [20, 20, 20], OBJECT_NAME, display_wireframe=True)
#     app_0.save_project(file_name=str(AEDT_PATH))
#     app_0.close_project(app_0.project_name)

#     # Load the project with the extension
#     add_app(application=Hfss, just_open=True)
#     assert main(asdict(DATA))
#     app = get_pyaedt_app()

#     # Assert that the object was loaded correctly
#     assert 1 == len(app.modeler.object_list)
#     assert OBJECT_NAME == app.modeler.object_list[0].name
